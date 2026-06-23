import aiosqlite
import logging 
from datetime import date 

logger = logging.getLogger(__name__)
DB_PATH = "archigen.db"

async def init_db():
    """ 
        Function which initializes the SQLite DB and creates the Rate_Limit table
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
                         CREATE TABLE IF NOT EXISTS rate_limits (
                             user_id TEXT PRIMARY KEY,
                             date TEXT, 
                             count INTEGER
                         )
                         """)
        
        await db.commit()
    
    logger.info("DB initialized successfully")
    
async def check_rate_limits(user_id: str, limit: int = 5) -> bool:
    """  
        Returns True if the User is under their Daily Limit, Else False
    """
    
    today = date.today().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT date, count FROM rate_limits WHERE user_id = ?", (user_id, )) as cursor:
            row = await cursor.fetchone()
            if not row:
                return True
            
            if row[0] != today:
                return True #It's a New day
            
            return row[1] < limit 
        
async def increment_rate_limit(user_id: str):
    """
        Function which Increment's the user generation count for today
    """
    
    today = date.today().isoformat()
    
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT count FROM rate_limits WHERE user_id = ? AND date = ?", (user_id, today)) as cursor:
            
            row = await cursor.fetchone()
            
            #Insert's new user with count 1
            if not row:
                await db.execute(
                    "INSERT INTO rate_limits (user_id, date, count) VALUES (?, ?, 1)", (user_id, today)
                )
                
            else:
                await db.execute("UPDATE rate_limits SET count = count + 1 WHERE user_id = ? AND date = ?", (user_id, today))
                
            await db.commit()
            
            