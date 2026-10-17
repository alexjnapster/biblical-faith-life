"""Owner-bound local SQLite library. The caller is the local OS user, not a remote tenant."""
from pathlib import Path
import sqlite3
import os
import json
import uuid
import re
import unicodedata
from .engines import sha

def terms(text):
    return set(re.findall(r'[^\W_]+',unicodedata.normalize('NFKC',text).casefold(),re.UNICODE))

class KnowledgeBase:
    def __init__(self, directory, owner):
        if not isinstance(owner,str) or not owner.strip(): raise ValueError('Owner is required')
        directory=Path(directory)
        if directory.is_symlink(): raise ValueError('Library directory cannot be a symlink')
        directory.mkdir(parents=True,exist_ok=True,mode=0o700)
        self.path=directory/'library.sqlite3'
        if self.path.is_symlink(): raise ValueError('Library file cannot be a symlink')
        existed=self.path.exists() and self.path.stat().st_size>0
        if self.path.exists() and self.path.stat().st_nlink>1:raise ValueError('Library file cannot have hard links')
        self.db=sqlite3.connect(self.path)
        # Inspect owner before schema creation or permission changes. A refused
        # open must not adopt or mutate another library (or an unrelated DB).
        if existed:
            try:prior=self.db.execute("SELECT value FROM meta WHERE key='owner'").fetchone()
            except sqlite3.DatabaseError:
                self.db.close();raise ValueError('Existing database is not an owned biblical library') from None
            if not prior:
                self.db.close();raise ValueError('Existing library has no owner metadata')
            if prior[0]!=owner:
                self.db.close();raise PermissionError('Library belongs to a different local owner')
            required={
                'meta':[('key','TEXT',1),('value','TEXT',0)],
                'versions':[('doc_id','TEXT',1),('version','INTEGER',2),('title','TEXT',0),('language','TEXT',0),('locator','TEXT',0),('content','TEXT',0),('hash','TEXT',0),('metadata','TEXT',0),('created_at','TEXT',0)],
                'tokens':[('token','TEXT',1),('doc_id','TEXT',2),('version','INTEGER',3)]}
            for table,columns in required.items():
                # Names are static constants, never interpolated user input.
                actual=[(r[1],r[2].upper(),r[5]) for r in self.db.execute('PRAGMA table_info('+table+')')]
                if actual!=columns:
                    self.db.close();raise ValueError('Existing database schema is not a biblical library')
            marker=self.db.execute("SELECT value FROM meta WHERE key='library_kind'").fetchone()
            if marker and marker[0]!='biblical-faith-life':
                self.db.close();raise ValueError('Existing database belongs to a different application')
        os.chmod(directory,0o700);os.chmod(self.path,0o600)
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('''CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY,value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS versions (doc_id TEXT NOT NULL,version INTEGER NOT NULL,title TEXT NOT NULL,language TEXT NOT NULL,locator TEXT NOT NULL,content TEXT NOT NULL,hash TEXT NOT NULL,metadata TEXT NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY(doc_id,version));
        CREATE TABLE IF NOT EXISTS tokens (token TEXT NOT NULL,doc_id TEXT NOT NULL,version INTEGER NOT NULL,PRIMARY KEY(token,doc_id,version),FOREIGN KEY(doc_id,version) REFERENCES versions(doc_id,version));''')
        prior=self.db.execute("SELECT value FROM meta WHERE key='owner'").fetchone()
        if prior and prior[0]!=owner:
            self.db.close();raise PermissionError('Library belongs to a different local owner')
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO meta VALUES ('owner',?)",(owner,))
            self.db.execute("INSERT OR IGNORE INTO meta VALUES ('library_kind','biblical-faith-life')")
            self.db.execute("INSERT OR IGNORE INTO meta VALUES ('schema_version','1')")
        self.owner=owner

    def close(self): self.db.close()

    def ingest(self,title,content,language,locator,doc_id=None,metadata=None,private=False,consent=False):
        if type(private)!=bool or type(consent)!=bool:raise ValueError('Privacy and consent must be actual booleans')
        if private and consent is not True: raise PermissionError('Explicit consent is required for private records')
        if language not in {'uk','en','ru'}: raise ValueError('Unsupported language')
        if any(not isinstance(x,str) or not x.strip() for x in (title,content,locator)): raise ValueError('Title, content, and locator are required')
        if len(content.encode())>8*1024*1024: raise ValueError('Document exceeds 8 MiB')
        if metadata is not None and not isinstance(metadata,dict):raise ValueError('Metadata must be an object')
        metadata=dict(metadata or {});metadata['private']=private
        encoded_metadata=json.dumps(metadata,ensure_ascii=False,sort_keys=True)
        h=sha(content)
        with self.db:
            duplicate=self.db.execute('SELECT doc_id,version FROM versions WHERE hash=? ORDER BY version DESC LIMIT 1',(h,)).fetchone()
            if doc_id is None: doc_id=str(uuid.uuid4())
            else:
                latest=self.db.execute('SELECT version,title,language,locator,hash,metadata FROM versions WHERE doc_id=? ORDER BY version DESC LIMIT 1',(doc_id,)).fetchone()
                if latest is None:raise KeyError('Unknown document ID')
                # Only an identical current version is an idempotent no-op.
                # Restoring historical text or changing provenance creates a
                # new current version and never rewrites the original.
                if latest[1:5]==(title,language,locator,h) and json.loads(latest[5])==metadata:
                    return {'doc_id':doc_id,'version':latest[0],'sha256':h,'duplicate':True,'created':False,'duplicate_of':{'doc_id':doc_id,'version':latest[0]}}
            version=self.db.execute('SELECT COALESCE(MAX(version),0)+1 FROM versions WHERE doc_id=?',(doc_id,)).fetchone()[0]
            self.db.execute('INSERT INTO versions(doc_id,version,title,language,locator,content,hash,metadata) VALUES (?,?,?,?,?,?,?,?)',(doc_id,version,title,language,locator,content,h,encoded_metadata))
            self.db.executemany('INSERT INTO tokens VALUES (?,?,?)',[(t,doc_id,version) for t in terms(title+' '+content)])
        return {'doc_id':doc_id,'version':version,'sha256':h,'duplicate':bool(duplicate),'created':True,'duplicate_of':{'doc_id':duplicate[0],'version':duplicate[1]} if duplicate else None}

    def get(self,doc_id,version=None):
        if version is None:
            row=self.db.execute('SELECT * FROM versions WHERE doc_id=? ORDER BY version DESC LIMIT 1',(doc_id,)).fetchone()
        else: row=self.db.execute('SELECT * FROM versions WHERE doc_id=? AND version=?',(doc_id,version)).fetchone()
        if not row: raise KeyError('Document/version not found')
        keys=['doc_id','version','title','language','locator','content','sha256','metadata','created_at']; result=dict(zip(keys,row)); result['metadata']=json.loads(result['metadata'])
        if sha(result['content'])!=result['sha256']: raise ValueError('Stored document integrity failure')
        return result

    def search(self,query,limit=10):
        ts=sorted(terms(query))
        if not ts: return []
        if len(ts)>100 or type(limit)!=int or not 1<=limit<=100: raise ValueError('Query or result limit exceeds bounds')
        slots=','.join('?' for _ in ts)
        rows=self.db.execute('SELECT t.doc_id,t.version,COUNT(*) score FROM tokens t WHERE t.token IN ('+slots+') AND t.version=(SELECT MAX(v.version) FROM versions v WHERE v.doc_id=t.doc_id) GROUP BY t.doc_id,t.version ORDER BY score DESC,t.doc_id LIMIT ?',ts+[limit]).fetchall()
        results=[]
        for doc_id,version,score in rows:
            d=self.get(doc_id,version);d['score']=score
            # Preserve exact original text, including script and punctuation.
            normalized=d['content'].casefold(); positions=[normalized.find(t) for t in ts if t in normalized];start=max(0,min(positions)-80) if positions else 0
            d['excerpt']=d['content'][start:start+500];results.append(d)
        return results
