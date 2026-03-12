import telebot
from telebot import types
import pg_adapter as aiosqlite  # Railway PostgreSQL adapter
import asyncio
import random
import os
import threading
from datetime import datetime, time

# Bot tokenini bu yerga kiriting
# Railway: DATABASE_URL va BOT_TOKEN env vars dan olinadi
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8310548897:AAG4khPevfikVGZdIo-p4ZMPF7vZq-r4eXM")
# Admin ID sini bu yerga kiriting
ADMIN_ID = int(os.environ.get("ADMIN_ID", "8296061905"))  # Railway: env var
CHANNEL_USERNAME = "@MatematikaQuizchi"


# Majburiy obuna kanallari (istalgancha qo'shish mumkin)
FORCE_SUB_CHANNELS = [
    {"username": "@MatematikaQuizchi", "name": "Matematika Quizchi"},
    # {"username": "@ikkinchi_kanal", "name": "Yangiliklar"},  # Qo'shimcha kanal
    # {"username": "@uchinchi_kanal", "name": "Darsliklar"},   # Yana bir kanal
]

# Majburiy obunani yoqish/o'chirish
FORCE_SUB_ENABLED = True  # True = yoqiq, False = o'chirilgan

# Darajalar sozlamalari
LEVELS = {
    1: {"name": "🌱 Yangi boshlovchi", "min": 0, "max": 100},
    2: {"name": "📚 O'rganuvchi", "min": 100, "max": 300},
    3: {"name": "🎓 Bilimdon", "min": 300, "max": 600},
    4: {"name": "💎 Mutaxassis", "min": 600, "max": 1000},
    5: {"name": "👑 Ustoz", "min": 1000, "max": 2000},
    6: {"name": "🏆 Professor", "min": 2000, "max": 5000},
    7: {"name": "⭐ Akademik", "min": 5000, "max": float('inf')}
}


# ==================== YUTUQLAR RO'YXATI ====================
# Joylashtirish: Bot sozlamalaridan keyin (25-qator atrofiga)

ACHIEVEMENTS = {
    # Asosiy yutuqlar
    'first_quiz': {
        'name': '🎯 Birinchi Quiz',
        'description': 'Birinchi quizni yechish',
        'xp_reward': 50,
        'emoji': '🎯'
    },
    'quiz_master_10': {
        'name': '📚 Quiz O\'quvchisi',
        'description': '10 ta quiz yechish',
        'xp_reward': 100,
        'emoji': '📚'
    },
    'quiz_master_50': {
        'name': '🎓 Quiz Mutaxassisi',
        'description': '50 ta quiz yechish',
        'xp_reward': 300,
        'emoji': '🎓'
    },
    'quiz_master_100': {
        'name': '👑 Quiz Ustasi',
        'description': '100 ta quiz yechish',
        'xp_reward': 500,
        'emoji': '👑'
    },
    
    # Perfectionist
    'perfect_quiz': {
        'name': '💯 Perfectionist',
        'description': '10/10 to\'g\'ri javob',
        'xp_reward': 100,
        'emoji': '💯'
    },
    
    # Streak yutuqlari
    'streak_3': {
        'name': '🔥 Ketma-ket 3 kun',
        'description': '3 kun ketma-ket quiz yechish',
        'xp_reward': 50,
        'emoji': '🔥'
    },
    'streak_7': {
        'name': '⚡ Streak Master',
        'description': '7 kun ketma-ket quiz yechish',
        'xp_reward': 150,
        'emoji': '⚡'
    },
    'streak_30': {
        'name': '💎 Streak Legend',
        'description': '30 kun ketma-ket quiz yechish',
        'xp_reward': 500,
        'emoji': '💎'
    },
    
    # Tezkor Quiz
    'speed_master': {
        'name': '🚀 Speed Demon',
        'description': 'Tezkor quizda 90+ ball',
        'xp_reward': 100,
        'emoji': '🚀'
    },
    
    # PvP yutuqlari
    'pvp_first_win': {
        'name': '⚔️ Birinchi G\'alaba',
        'description': 'Birinchi PvP g\'alabasi',
        'xp_reward': 50,
        'emoji': '⚔️'
    },
    'pvp_champion': {
        'name': '🏆 PvP Champion',
        'description': '10 ta PvP g\'alabasi',
        'xp_reward': 200,
        'emoji': '🏆'
    },
    'pvp_legend': {
        'name': '👑 PvP Legend',
        'description': '50 ta PvP g\'alabasi',
        'xp_reward': 500,
        'emoji': '👑'
    },
    
    # Clan yutuqlari
    'clan_founder': {
        'name': '🛡️ Clan Asoschisi',
        'description': 'Clan yaratish',
        'xp_reward': 100,
        'emoji': '🛡️'
    },
    'clan_hero': {
        'name': '⭐ Clan Qahramoni',
        'description': 'Clan uchun 1000+ XP yig\'ish',
        'xp_reward': 200,
        'emoji': '⭐'
    },
    
    # Referal yutuqlari
    'ambassador': {
        'name': '👥 Ambassador',
        'description': '10 ta referal',
        'xp_reward': 200,
        'emoji': '👥'
    },
    'influencer': {
        'name': '🌟 Influencer',
        'description': '25 ta referal',
        'xp_reward': 500,
        'emoji': '🌟'
    },
    
    # Daraja yutuqlari
    'level_5': {
        'name': '🎖️ Mutaxassis',
        'description': '5-darajaga chiqish',
        'xp_reward': 200,
        'emoji': '🎖️'
    },
    'level_7': {
        'name': '🏅 Professor',
        'description': '7-darajaga chiqish',
        'xp_reward': 500,
        'emoji': '🏅'
    },
    
    # O'rganish
    'reader': {
        'name': '📖 Kitobxon',
        'description': '5 ta mavzu o\'qish',
        'xp_reward': 100,
        'emoji': '📖'
    },
    
    # XP yutuqlari
    'xp_1000': {
        'name': '💫 XP Collecter',
        'description': '1,000 XP to\'plash',
        'xp_reward': 100,
        'emoji': '💫'
    },
    'xp_5000': {
        'name': '✨ XP Master',
        'description': '5,000 XP to\'plash',
        'xp_reward': 300,
        'emoji': '✨'
    },
    'xp_10000': {
        'name': '⭐ XP Legend',
        'description': '10,000 XP to\'plash',
        'xp_reward': 500,
        'emoji': '⭐'
    }
}



bot = telebot.TeleBot(BOT_TOKEN)

# Global o'zgaruvchilar
user_sessions = {}
admin_sessions = {}
broadcast_sessions = {}
pvp_sessions = {}  # YANGI
pvp_invites = {}   # YANGI
speed_quiz_sessions = {} 
clan_invites = {}  # Clan takliflari
group_quiz_sessions = {}  # Guruh quiz sessiyalari


DB_PATH = "quiz_bot.db"


# ==================== DATABASE ====================
async def init_db():
    """Ma'lumotlar bazasini yaratish"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Savollar jadvali
        await db.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                explanation TEXT
            )
        ''')
        
        # Foydalanuvchilar jadvali
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                correct_answers INTEGER DEFAULT 0,
                wrong_answers INTEGER DEFAULT 0,
                total_quizzes INTEGER DEFAULT 0
            )
        ''')
        
        await db.commit()

# ==================== DATABASE - MAVSUM JADVALI ====================
# init_db funksiyasiga qo'shing (CREATE TABLE qismida)

async def init_season_table():
    """Mavsum statistikasi jadvali"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Mavsum statistikasi jadvali
        await db.execute('''
            CREATE TABLE IF NOT EXISTS season_stats (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                season_correct INTEGER DEFAULT 0,
                season_wrong INTEGER DEFAULT 0,
                season_quizzes INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Mavsum tarixi jadvali
        await db.execute('''
            CREATE TABLE IF NOT EXISTS season_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                season_number INTEGER,
                season_name TEXT,
                start_date TEXT,
                end_date TEXT,
                winner_id INTEGER,
                winner_username TEXT,
                winner_score INTEGER
            )
        ''')
        
        # Mavsum sozlamalari jadvali
        await db.execute('''
            CREATE TABLE IF NOT EXISTS season_config (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                current_season INTEGER DEFAULT 1,
                season_name TEXT DEFAULT 'Mavsum 1',
                season_start TEXT,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        # Agar mavsum sozlamalari bo'sh bo'lsa, birinchi mavsumni boshlash
        cursor = await db.execute('SELECT COUNT(*) FROM season_config')
        count = (await cursor.fetchone())[0]
        
        if count == 0:
            from datetime import datetime
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            await db.execute(
                'INSERT INTO season_config (id, current_season, season_name, season_start, is_active) VALUES (1, 1, ?, ?, 1)',
                ('Mavsum 1', now)
            )
        
        await db.commit()



# ==================== 2-QISM: DATABASE JADVALLARI ====================
# Joylashtirish: init_speed_quiz_table dan keyin (110-qator atrofiga)

async def init_clan_tables():
    """Clan jadvallari"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Clan jadvali
        await db.execute('''
            CREATE TABLE IF NOT EXISTS clans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                tag TEXT UNIQUE NOT NULL,
                description TEXT,
                leader_id INTEGER NOT NULL,
                created_date TEXT,
                total_xp INTEGER DEFAULT 0,
                member_count INTEGER DEFAULT 1,
                max_members INTEGER DEFAULT 50,
                FOREIGN KEY (leader_id) REFERENCES users(user_id)
            )
        ''')
        
        # Clan a'zolari
        await db.execute('''
            CREATE TABLE IF NOT EXISTS clan_members (
                user_id INTEGER PRIMARY KEY,
                clan_id INTEGER NOT NULL,
                role TEXT DEFAULT 'member',
                joined_date TEXT,
                contribution_xp INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (clan_id) REFERENCES clans(id)
            )
        ''')
        
        await db.commit()


# ==================== 1-QISM: DATABASE JADVALI ====================
# Joylashtirish: init_reminder_table dan keyin (160-qator atrofiga)

async def init_achievements_table():
    """Yutuqlar jadvali"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Foydalanuvchi yutuqlari
        await db.execute('''
            CREATE TABLE IF NOT EXISTS user_achievements (
                user_id INTEGER,
                achievement_id TEXT,
                unlocked_date TEXT,
                PRIMARY KEY (user_id, achievement_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Profil sozlamalari
        await db.execute('''
            CREATE TABLE IF NOT EXISTS profile_settings (
                user_id INTEGER PRIMARY KEY,
                avatar_emoji TEXT DEFAULT '👤',
                custom_title TEXT,
                profile_color TEXT DEFAULT 'blue',
                bio TEXT,
                topics_read INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        await db.commit()


# ==================== DATABASE JADVALI ====================
# Joylashtirish: init_achievements_table dan keyin (180-qator atrofiga)

async def init_group_quiz_table():
    """Guruh quiz jadvali"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Guruh quiz statistikasi
        await db.execute('''
            CREATE TABLE IF NOT EXISTS group_quiz_stats (
                user_id INTEGER,
                group_id INTEGER,
                total_games INTEGER DEFAULT 0,
                total_score INTEGER DEFAULT 0,
                best_score INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, group_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Guruh quiz tarixi
        await db.execute('''
            CREATE TABLE IF NOT EXISTS group_quiz_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER,
                quiz_date TEXT,
                total_participants INTEGER,
                winner_id INTEGER,
                winner_score INTEGER
            )
        ''')
        
        await db.commit()


# ==================== DATABASE FUNKSIYALARI ====================
# Joylashtirish: Achievements funksiyalaridan keyin (700-qator atrofiga)

async def update_group_quiz_stats(user_id, group_id, score):
    """Guruh quiz statistikasini yangilash"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Foydalanuvchini qo'shish
        await db.execute(
            'INSERT INTO group_quiz_stats (user_id, group_id) VALUES (?, ?)',
            (user_id, group_id)
        )
        
        # Statistikani yangilash
        await db.execute('''
            UPDATE group_quiz_stats 
            SET total_games = total_games + 1,
                total_score = total_score + ?,
                best_score = MAX(best_score, ?)
            WHERE user_id = ? AND group_id = ?
        ''', (score, score, user_id, group_id))
        
        await db.commit()


async def save_group_quiz_history(group_id, participants, winner_id, winner_score):
    """Guruh quiz tarixiga saqlash"""
    async with aiosqlite.connect(DB_PATH) as db:
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        await db.execute('''
            INSERT INTO group_quiz_history 
            (group_id, quiz_date, total_participants, winner_id, winner_score)
            VALUES (?, ?, ?, ?, ?)
        ''', (group_id, now, participants, winner_id, winner_score))
        
        await db.commit()


async def get_group_leaderboard(group_id, limit=10):
    """Guruh reytingi"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT g.user_id, g.total_games, g.best_score, g.total_score
            FROM group_quiz_stats g
            WHERE g.group_id = ?
            ORDER BY g.best_score DESC, g.total_games DESC
            LIMIT ?
        ''', (group_id, limit))
        return await cursor.fetchall()

                                                                

# ==================== 2-QISM: DATABASE JADVALI ====================
# Joylashtirish: init_db dan keyin (90-qator atrofiga)

async def init_speed_quiz_table():
    """Tezkor quiz jadvali"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS speed_quiz_stats (
                user_id INTEGER PRIMARY KEY,
                games_played INTEGER DEFAULT 0,
                best_time INTEGER DEFAULT 999,
                best_score INTEGER DEFAULT 0,
                total_score INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        await db.commit()


# ==================== DATABASE - DARAJALAR ====================
# init_db dan keyin qo'shing

async def init_levels_table():
    """Darajalar jadvali va barcha ustunlarni tekshirish"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in await cursor.fetchall()]

        # Asosiy statistika ustunlari (eski DB uchun migration)
        if 'correct_answers' not in columns:
            await db.execute('ALTER TABLE users ADD COLUMN correct_answers INTEGER DEFAULT 0')
        if 'wrong_answers' not in columns:
            await db.execute('ALTER TABLE users ADD COLUMN wrong_answers INTEGER DEFAULT 0')
        if 'total_quizzes' not in columns:
            await db.execute('ALTER TABLE users ADD COLUMN total_quizzes INTEGER DEFAULT 0')
        # Daraja va XP ustunlari
        if 'level' not in columns:
            await db.execute('ALTER TABLE users ADD COLUMN level INTEGER DEFAULT 1')
        if 'xp' not in columns:
            await db.execute('ALTER TABLE users ADD COLUMN xp INTEGER DEFAULT 0')

        await db.commit()
 

# ==================== DATABASE - PVP JADVALI ====================

async def init_pvp_table():
    """PvP statistika jadvali"""
    async with aiosqlite.connect(DB_PATH) as db:
        # PvP statistika jadvali
        await db.execute('''
            CREATE TABLE IF NOT EXISTS pvp_stats (
                user_id INTEGER PRIMARY KEY,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                draws INTEGER DEFAULT 0,
                total_battles INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # PvP tarixi
        await db.execute('''
            CREATE TABLE IF NOT EXISTS pvp_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player1_id INTEGER,
                player2_id INTEGER,
                player1_score INTEGER,
                player2_score INTEGER,
                winner_id INTEGER,
                battle_date TEXT,
                FOREIGN KEY (player1_id) REFERENCES users(user_id),
                FOREIGN KEY (player2_id) REFERENCES users(user_id)
            )
        ''')
        
        await db.commit()

       

# ==================== DATABASE - O'RGANISH JADVALI ====================
# init_db funksiyasidan keyin qo'shing

async def init_learning_table():
    """O'rganish bo'limi jadvali"""
    async with aiosqlite.connect(DB_PATH) as db:
        # O'rganish mavzulari jadvali
        await db.execute('''
            CREATE TABLE IF NOT EXISTS learning_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_date TEXT,
                order_num INTEGER DEFAULT 0
            )
        ''')
        await db.commit()                
        
      
# ==================== REFERAL TIZIMI ====================
# Bu kodni asosiy kodning 60-qatoridan keyin joylashtiring (init_db funksiyasidan keyin)

async def init_referral_table():
    """Referal jadvali yaratish"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Users jadvaliga referal maydonlarini qo'shish
        await db.execute('''
            CREATE TABLE IF NOT EXISTS referrals (
                user_id INTEGER PRIMARY KEY,
                referrer_id INTEGER,
                referral_count INTEGER DEFAULT 0,
                bonus_points INTEGER DEFAULT 0,
                FOREIGN KEY (referrer_id) REFERENCES users(user_id)
            )
        ''')
        await db.commit()


async def add_referral(user_id, referrer_id):
    """Referal qo'shish"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Yangi foydalanuvchini referal jadvaliga qo'shish
        await db.execute(
            'INSERT INTO referrals (user_id, referrer_id) VALUES (?, ?)',
            (user_id, referrer_id)
        )
        
        # Taklif qilgan odamning referal sonini oshirish
        await db.execute(
            'UPDATE referrals SET referral_count = referral_count + 1 WHERE user_id = ?',
            (referrer_id,)
        )
        
        # Bonus ball berish (har bir referal uchun 5 ball)
        await db.execute(
            'UPDATE referrals SET bonus_points = bonus_points + 5 WHERE user_id = ?',
            (referrer_id,)
        )
        
        await db.commit()


async def get_referral_stats(user_id):
    """Referal statistikasini olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Foydalanuvchini referal jadvaliga qo'shish (agar yo'q bo'lsa)
        await db.execute(
            'INSERT INTO referrals (user_id, referrer_id) VALUES (?, NULL)',
            (user_id,)
        )
        await db.commit()
        
        cursor = await db.execute(
            'SELECT referral_count, bonus_points FROM referrals WHERE user_id = ?',
            (user_id,)
        )
        result = await cursor.fetchone()
        return result if result else (0, 0)


async def get_referral_leaderboard(limit=10):
    """Top referalchilar ro'yxati"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT u.username, r.referral_count, r.bonus_points
            FROM referrals r
            JOIN users u ON r.user_id = u.user_id
            WHERE r.referral_count > 0
            ORDER BY r.referral_count DESC
            LIMIT ?
        ''', (limit,))
        return await cursor.fetchall()



async def add_user(user_id, username):
    """Yangi foydalanuvchi qo'shish"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT INTO users (user_id, username) VALUES (?, ?)',
            (user_id, username)
        )
        await db.commit()


async def get_user_stats(user_id):
    """Foydalanuvchi statistikasini olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT correct_answers, wrong_answers, total_quizzes FROM users WHERE user_id = ?',
            (user_id,)
        )
        result = await cursor.fetchone()
        return result if result else (0, 0, 0)


async def update_user_stats(user_id, correct, wrong):
    """Foydalanuvchi statistikasini yangilash"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            UPDATE users 
            SET correct_answers = correct_answers + ?,
                wrong_answers = wrong_answers + ?,
                total_quizzes = total_quizzes + 1
            WHERE user_id = ?
        ''', (correct, wrong, user_id))
        await db.commit()

# Bu funksiyani database bo'limiga qo'shing (get_user_stats dan keyin)

async def get_overall_statistics():
    """Umumiy statistika - barcha ma'lumotlar"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Umumiy foydalanuvchilar soni
        cursor = await db.execute('SELECT COUNT(*) FROM users')
        total_users = (await cursor.fetchone())[0]
        
        # Umumiy quizlar soni
        cursor = await db.execute('SELECT SUM(total_quizzes) FROM users')
        total_quizzes = (await cursor.fetchone())[0] or 0
        
        # Umumiy savollar soni
        cursor = await db.execute('SELECT COUNT(*) FROM questions')
        total_questions = (await cursor.fetchone())[0]
        
        # Top 20 foydalanuvchilar (to'g'ri javoblar bo'yicha)
        cursor = await db.execute('''
            SELECT username, correct_answers, wrong_answers, total_quizzes,
                   (correct_answers * 100.0 / NULLIF(correct_answers + wrong_answers, 0)) as accuracy
            FROM users
            WHERE correct_answers > 0
            ORDER BY correct_answers DESC
            LIMIT 20
        ''')
        top_users = await cursor.fetchall()
        
        return {
            'total_users': total_users,
            'total_quizzes': total_quizzes,
            'total_questions': total_questions,
            'top_users': top_users
        }



# ==================== 2-QISM: DATABASE FUNKSIYALARI ====================
# Joylashtirish: Eslatma funksiyalaridan keyin (500-qator atrofiga)

async def unlock_achievement(user_id, achievement_id):
    """Yutuqni ochish"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Oldin ochilganmi tekshirish
        cursor = await db.execute(
            'SELECT achievement_id FROM user_achievements WHERE user_id = ? AND achievement_id = ?',
            (user_id, achievement_id)
        )
        
        if await cursor.fetchone():
            return False  # Allaqachon ochilgan
        
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Yutuqni qo'shish
        await db.execute(
            'INSERT INTO user_achievements (user_id, achievement_id, unlocked_date) VALUES (?, ?, ?)',
            (user_id, achievement_id, now)
        )
        await db.commit()
        
        return True  # Yangi yutuq


async def get_user_achievements(user_id):
    """Foydalanuvchi yutuqlarini olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT achievement_id, unlocked_date FROM user_achievements WHERE user_id = ?',
            (user_id,)
        )
        return await cursor.fetchall()


async def check_and_unlock_achievements(user_id):
    """Yutuqlarni tekshirish va ochish"""
    unlocked = []
    
    # Statistikani olish
    correct, wrong, total_quizzes = await get_user_stats(user_id)
    level, xp = await get_user_level_info(user_id)
    streak_data = await get_reminder_settings(user_id)
    _, _, streak, _ = streak_data
    pvp_stats = await get_pvp_stats(user_id)
    pvp_wins = pvp_stats[0]
    referal_data = await get_referral_stats(user_id)
    referal_count = referal_data[0]
    
    # Yutuqlarni tekshirish
    checks = [
        # Asosiy
        ('first_quiz', total_quizzes >= 1),
        ('quiz_master_10', total_quizzes >= 10),
        ('quiz_master_50', total_quizzes >= 50),
        ('quiz_master_100', total_quizzes >= 100),
        
        # Perfectionist (10/10 to'g'ri javob) - buni alohida tekshirish kerak
        
        # Streak
        ('streak_3', streak >= 3),
        ('streak_7', streak >= 7),
        ('streak_30', streak >= 30),
        
        # PvP
        ('pvp_first_win', pvp_wins >= 1),
        ('pvp_champion', pvp_wins >= 10),
        ('pvp_legend', pvp_wins >= 50),
        
        # Referal
        ('ambassador', referal_count >= 10),
        ('influencer', referal_count >= 25),
        
        # Daraja
        ('level_5', level >= 5),
        ('level_7', level >= 7),
        
        # XP
        ('xp_1000', xp >= 1000),
        ('xp_5000', xp >= 5000),
        ('xp_10000', xp >= 10000),
    ]
    
    for achievement_id, condition in checks:
        if condition:
            if await unlock_achievement(user_id, achievement_id):
                unlocked.append(achievement_id)
    
    return unlocked


async def get_profile_settings(user_id):
    """Profil sozlamalarini olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT INTO profile_settings (user_id) VALUES (?)',
            (user_id,)
        )
        await db.commit()
        
        cursor = await db.execute(
            'SELECT avatar_emoji, custom_title, profile_color, bio, topics_read FROM profile_settings WHERE user_id = ?',
            (user_id,)
        )
        result = await cursor.fetchone()
        return result if result else ('👤', None, 'blue', None, 0)


async def update_profile_settings(user_id, **kwargs):
    """Profil sozlamalarini yangilash"""
    async with aiosqlite.connect(DB_PATH) as db:
        for key, value in kwargs.items():
            await db.execute(
                f'UPDATE profile_settings SET {key} = ? WHERE user_id = ?',
                (value, user_id)
            )
        await db.commit()


async def init_reminder_table():
    """Eslatma va streak jadvali"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS user_reminders (
                user_id INTEGER PRIMARY KEY,
                reminder_enabled INTEGER DEFAULT 0,
                reminder_time TEXT DEFAULT '09:00',
                streak INTEGER DEFAULT 0,
                best_streak INTEGER DEFAULT 0,
                last_quiz_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        await db.commit()


async def get_reminder_settings(user_id):
    """Foydalanuvchi eslatma sozlamalarini olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT INTO user_reminders (user_id) VALUES (?)',
            (user_id,)
        )
        await db.commit()
        cursor = await db.execute(
            'SELECT reminder_enabled, reminder_time, streak, best_streak FROM user_reminders WHERE user_id = ?',
            (user_id,)
        )
        result = await cursor.fetchone()
        return result if result else (0, '09:00', 0, 0)


async def update_streak(user_id):
    """Streak ni yangilash"""
    from datetime import datetime, date
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT INTO user_reminders (user_id) VALUES (?)',
            (user_id,)
        )
        cursor = await db.execute(
            'SELECT streak, best_streak, last_quiz_date FROM user_reminders WHERE user_id = ?',
            (user_id,)
        )
        result = await cursor.fetchone()
        today_str = date.today().isoformat()

        if result:
            streak, best_streak, last_date = result
            if last_date == today_str:
                return streak  # Already counted today
            elif last_date and (date.today() - date.fromisoformat(last_date)).days == 1:
                streak += 1
            else:
                streak = 1
            best_streak = max(streak, best_streak or 0)
        else:
            streak, best_streak = 1, 1

        await db.execute(
            '''UPDATE user_reminders SET streak=?, best_streak=?, last_quiz_date=? WHERE user_id=?''',
            (streak, best_streak, today_str, user_id)
        )
        await db.commit()
        return streak


# ==================== 3-QISM: YUTUQ OLISH FUNKSIYASI ====================
# Har bir o'yin tugaganda chaqirish

async def give_achievement_reward(user_id, achievement_id):
    """Yutuq mukofotini berish"""
    achievement = ACHIEVEMENTS.get(achievement_id)
    
    if achievement:
        xp_reward = achievement['xp_reward']
        await update_user_xp(user_id, xp_reward)
        return xp_reward
    
    return 0


# ==================== 3-QISM: DATABASE FUNKSIYALARI ====================
# Joylashtirish: Database funksiyalar bo'limiga (200-qator atrofiga)

async def get_speed_quiz_stats(user_id):
    """Tezkor quiz statistikasi"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Foydalanuvchini qo'shish (agar yo'q bo'lsa)
        await db.execute(
            'INSERT INTO speed_quiz_stats (user_id) VALUES (?)',
            (user_id,)
        )
        await db.commit()
        
        cursor = await db.execute(
            'SELECT games_played, best_time, best_score, total_score FROM speed_quiz_stats WHERE user_id = ?',
            (user_id,)
        )
        result = await cursor.fetchone()
        return result if result else (0, 999, 0, 0)


async def update_speed_quiz_stats(user_id, time_taken, score):
    """Tezkor quiz statistikasini yangilash"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Hozirgi eng yaxshi natijalarni olish
        cursor = await db.execute(
            'SELECT best_time, best_score FROM speed_quiz_stats WHERE user_id = ?',
            (user_id,)
        )
        result = await cursor.fetchone()
        
        if result:
            best_time, best_score = result
            new_best_time = min(time_taken, best_time)
            new_best_score = max(score, best_score)
        else:
            new_best_time = time_taken
            new_best_score = score
        
        # Yangilash
        await db.execute('''
            UPDATE speed_quiz_stats 
            SET games_played = games_played + 1,
                best_time = ?,
                best_score = ?,
                total_score = total_score + ?
            WHERE user_id = ?
        ''', (new_best_time, new_best_score, score, user_id))
        
        await db.commit()
        
        # Rekord bo'ldi mi?
        return new_best_time == time_taken, new_best_score == score


async def get_speed_quiz_leaderboard(limit=10):
    """Tezkor quiz reytingi"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT u.username, s.best_score, s.best_time, s.games_played
            FROM speed_quiz_stats s
            JOIN users u ON s.user_id = u.user_id
            WHERE s.games_played > 0
            ORDER BY s.best_score DESC, s.best_time ASC
            LIMIT ?
        ''', (limit,))
        return await cursor.fetchall()



# ==================== 3-QISM: CLAN DATABASE FUNKSIYALARI ====================
# Joylashtirish: get_speed_quiz_leaderboard dan keyin (280-qator atrofiga)

async def create_clan(name, tag, description, leader_id):
    """Clan yaratish"""
    async with aiosqlite.connect(DB_PATH) as db:
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            cursor = await db.execute('''
                INSERT INTO clans (name, tag, description, leader_id, created_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, tag.upper(), description, leader_id, now))
            
            clan_id = cursor.lastrowid
            
            # Liderni a'zo qilish
            await db.execute('''
                INSERT INTO clan_members (user_id, clan_id, role, joined_date)
                VALUES (?, ?, 'leader', ?)
            ''', (leader_id, clan_id, now))
            
            await db.commit()
            return True, clan_id
        except Exception as e:
            return False, str(e)


async def get_user_clan(user_id):
    """Foydalanuvchining clani"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT c.id, c.name, c.tag, c.description, c.total_xp, c.member_count, cm.role, c.max_members
            FROM clan_members cm
            JOIN clans c ON cm.clan_id = c.id
            WHERE cm.user_id = ?
        ''', (user_id,))
        return await cursor.fetchone()


async def get_clan_by_tag(tag):
    """Clan tag orqali qidirish"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT id, name, tag, description, leader_id, total_xp, member_count, max_members
            FROM clans
            WHERE tag = ?
        ''', (tag.upper(),))
        return await cursor.fetchone()


async def get_clan_by_id(clan_id):
    """Clan ID orqali olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT id, name, tag, description, leader_id, total_xp, member_count, max_members
            FROM clans
            WHERE id = ?
        ''', (clan_id,))
        return await cursor.fetchone()


async def join_clan(user_id, clan_id):
    """Clanga qo'shilish"""
    async with aiosqlite.connect(DB_PATH) as db:
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # A'zolar sonini tekshirish
        cursor = await db.execute(
            'SELECT member_count, max_members FROM clans WHERE id = ?',
            (clan_id,)
        )
        result = await cursor.fetchone()
        
        if not result:
            return False, "Clan topilmadi"
        
        member_count, max_members = result
        
        if member_count >= max_members:
            return False, f"Clan to'lgan (max: {max_members})"
        
        try:
            await db.execute('''
                INSERT INTO clan_members (user_id, clan_id, joined_date)
                VALUES (?, ?, ?)
            ''', (user_id, clan_id, now))
            
            await db.execute('''
                UPDATE clans SET member_count = member_count + 1 WHERE id = ?
            ''', (clan_id,))
            
            await db.commit()
            return True, "Muvaffaqiyatli qo'shildi"
        except Exception as e:
            return False, str(e)


async def leave_clan(user_id):
    """Clandan chiqish"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Clan ID ni olish
        cursor = await db.execute(
            'SELECT clan_id, role FROM clan_members WHERE user_id = ?',
            (user_id,)
        )
        result = await cursor.fetchone()
        
        if not result:
            return False, "Siz clanda emassiz"
        
        clan_id, role = result
        
        # Agar leader bo'lsa
        if role == 'leader':
            # Clan a'zolari sonini tekshirish
            cursor = await db.execute(
                'SELECT COUNT(*) FROM clan_members WHERE clan_id = ?',
                (clan_id,)
            )
            member_count = (await cursor.fetchone())[0]
            
            if member_count > 1:
                return False, "Avval liderlikni o'tkazing yoki barcha a'zolarni chiqarib yuboring"
            else:
                # Clanni o'chirish (faqat leader qolganda)
                await db.execute('DELETE FROM clans WHERE id = ?', (clan_id,))
        
        # A'zolikni o'chirish
        await db.execute('DELETE FROM clan_members WHERE user_id = ?', (user_id,))
        
        # Clan a'zolari sonini kamaytirish
        await db.execute(
            'UPDATE clans SET member_count = member_count - 1 WHERE id = ?',
            (clan_id,)
        )
        
        await db.commit()
        return True, "Muvaffaqiyatli chiqildi"


async def get_clan_members(clan_id):
    """Clan a'zolari"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT u.user_id, u.username, cm.role, cm.contribution_xp, u.level, u.xp
            FROM clan_members cm
            JOIN users u ON cm.user_id = u.user_id
            WHERE cm.clan_id = ?
            ORDER BY cm.contribution_xp DESC
        ''', (clan_id,))
        return await cursor.fetchall()


async def update_clan_xp(user_id, xp_gained):
    """Clan XP ni yangilash"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Foydalanuvchining clan ID sini olish
        cursor = await db.execute(
            'SELECT clan_id FROM clan_members WHERE user_id = ?',
            (user_id,)
        )
        result = await cursor.fetchone()
        
        if result:
            clan_id = result[0]
            
            # Clan XP ni oshirish
            await db.execute(
                'UPDATE clans SET total_xp = total_xp + ? WHERE id = ?',
                (xp_gained, clan_id)
            )
            
            # A'zoning contribution ni oshirish
            await db.execute(
                'UPDATE clan_members SET contribution_xp = contribution_xp + ? WHERE user_id = ?',
                (xp_gained, user_id)
            )
            
            await db.commit()


async def get_clan_leaderboard(limit=10):
    """Clan reytingi"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT name, tag, total_xp, member_count
            FROM clans
            ORDER BY total_xp DESC
            LIMIT ?
        ''', (limit,))
        return await cursor.fetchall()


async def kick_member(clan_id, user_id):
    """A'zoni chiqarib yuborish"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('DELETE FROM clan_members WHERE user_id = ?', (user_id,))
        await db.execute(
            'UPDATE clans SET member_count = member_count - 1 WHERE id = ?',
            (clan_id,)
        )
        await db.commit()



# ==================== DATABASE FUNKSIYALARI ====================
# Database bo'limiga qo'shing

async def get_season_info():
    """Hozirgi mavsum ma'lumotlari"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT current_season, season_name, season_start, is_active FROM season_config WHERE id = 1')
        return await cursor.fetchone()


async def get_season_top_users(limit=20):
    """Mavsum top foydalanuvchilari"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT username, season_correct, season_wrong, season_quizzes,
                   (season_correct * 100.0 / NULLIF(season_correct + season_wrong, 0)) as accuracy
            FROM season_stats
            WHERE season_correct > 0
            ORDER BY season_correct DESC
            LIMIT ?
        ''', (limit,))
        return await cursor.fetchall()


async def update_season_stats(user_id, username, correct, wrong):
    """Mavsum statistikasini yangilash"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Foydalanuvchini qo'shish (agar yo'q bo'lsa)
        await db.execute(
            'INSERT INTO season_stats (user_id, username) VALUES (?, ?)',
            (user_id, username)
        )
        
        # Statistikani yangilash
        await db.execute('''
            UPDATE season_stats 
            SET season_correct = season_correct + ?,
                season_wrong = season_wrong + ?,
                season_quizzes = season_quizzes + 1,
                username = ?
            WHERE user_id = ?
        ''', (correct, wrong, username, user_id))
        
        await db.commit()


async def reset_season_stats():
    """Mavsum statistikasini tozalash"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('DELETE FROM season_stats')
        await db.commit()


async def save_season_winner():
    """Mavsum g'olibini saqlash"""
    async with aiosqlite.connect(DB_PATH) as db:
        from datetime import datetime
        
        # Hozirgi mavsum ma'lumotlari
        season_info = await get_season_info()
        season_num, season_name, start_date, is_active = season_info
        
        # Top 1 foydalanuvchi
        cursor = await db.execute('''
            SELECT user_id, username, season_correct
            FROM season_stats
            ORDER BY season_correct DESC
            LIMIT 1
        ''')
        winner = await cursor.fetchone()
        
        if winner:
            winner_id, winner_username, winner_score = winner
            end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Tarixga saqlash
            await db.execute('''
                INSERT INTO season_history 
                (season_number, season_name, start_date, end_date, winner_id, winner_username, winner_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (season_num, season_name, start_date, end_date, winner_id, winner_username, winner_score))
            
            await db.commit()
            return winner_username, winner_score
        
        return None, None


async def start_new_season(season_name):
    """Yangi mavsumni boshlash"""
    async with aiosqlite.connect(DB_PATH) as db:
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Mavsum raqamini oshirish
        await db.execute('''
            UPDATE season_config 
            SET current_season = current_season + 1,
                season_name = ?,
                season_start = ?,
                is_active = 1
            WHERE id = 1
        ''', (season_name, now))
        
        await db.commit()


async def get_season_history(limit=10):
    """Mavsum tarixi"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT season_number, season_name, start_date, end_date, winner_username, winner_score
            FROM season_history
            ORDER BY season_number DESC
            LIMIT ?
        ''', (limit,))
        return await cursor.fetchall()


# ==================== DATABASE FUNKSIYALARI ====================
# Database bo'limiga qo'shing

async def get_all_topics():
    """Barcha mavzularni olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT id, title, order_num FROM learning_topics ORDER BY order_num ASC, id ASC'
        )
        return await cursor.fetchall()


async def get_topic_by_id(topic_id):
    """Mavzuni ID orqali olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT id, title, content FROM learning_topics WHERE id = ?',
            (topic_id,)
        )
        return await cursor.fetchone()


async def add_topic(title, content):
    """Yangi mavzu qo'shish"""
    async with aiosqlite.connect(DB_PATH) as db:
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        await db.execute(
            'INSERT INTO learning_topics (title, content, created_date) VALUES (?, ?, ?)',
            (title, content, now)
        )
        await db.commit()


async def delete_topic(topic_id):
    """Mavzuni o'chirish"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('DELETE FROM learning_topics WHERE id = ?', (topic_id,))
        await db.commit()


async def update_topic(topic_id, title, content):
    """Mavzuni tahrirlash"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'UPDATE learning_topics SET title = ?, content = ? WHERE id = ?',
            (title, content, topic_id)
        )
        await db.commit()


async def get_topics_count():
    """Mavzular sonini olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT COUNT(*) FROM learning_topics')
        return (await cursor.fetchone())[0]


# ==================== DARAJALAR FUNKSIYALARI ====================
# Database bo'limiga qo'shing

async def get_user_level_info(user_id):
    """Foydalanuvchi daraja ma'lumotlari"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT level, xp FROM users WHERE user_id = ?',
            (user_id,)
        )
        result = await cursor.fetchone()
        return result if result else (1, 0)


async def update_user_xp(user_id, xp_gained):
    """XP ni yangilash va darajani tekshirish"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Hozirgi level va XP
        cursor = await db.execute(
            'SELECT level, xp FROM users WHERE user_id = ?',
            (user_id,)
        )
        result = await cursor.fetchone()
        
        if not result:
            return None, None, False
        
        current_level, current_xp = result
        new_xp = current_xp + xp_gained
        
        # Yangi darajani hisoblash
        new_level = calculate_level(new_xp)
        level_up = new_level > current_level
        
        # Yangilash
        await db.execute(
            'UPDATE users SET level = ?, xp = ? WHERE user_id = ?',
            (new_level, new_xp, user_id)
        )
        await db.commit()
        
        return new_level, new_xp, level_up


def calculate_level(xp):
    """XP dan darajani hisoblash"""
    for level, info in sorted(LEVELS.items(), reverse=True):
        if xp >= info['min']:
            return level
    return 1


def get_level_name(level):
    """Daraja nomini olish"""
    return LEVELS.get(level, {}).get('name', '🌱 Yangi boshlovchi')


def get_next_level_xp(current_level):
    """Keyingi daraja uchun kerakli XP"""
    if current_level >= len(LEVELS):
        return None  # Maksimal daraja
    return LEVELS[current_level + 1]['min']


def calculate_xp_from_quiz(correct, wrong):
    """Quiz dan XP hisoblash"""
    # To'g'ri javob uchun 10 XP
    # Noto'g'ri javob uchun 0 XP
    # Bonus: agar 8+ to'g'ri bo'lsa +20 bonus XP
    base_xp = correct * 10
    bonus = 20 if correct >= 8 else 0
    return base_xp + bonus


async def get_top_users_by_level(limit=10):
    """Eng yuqori darajadagi foydalanuvchilar"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT username, level, xp
            FROM users
            WHERE xp > 0
            ORDER BY xp DESC
            LIMIT ?
        ''', (limit,))
        return await cursor.fetchall()


# ==================== PVP DATABASE FUNKSIYALARI ====================

async def get_pvp_stats(user_id):
    """PvP statistikasini olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Foydalanuvchini qo'shish
        await db.execute(
            'INSERT INTO pvp_stats (user_id) VALUES (?)',
            (user_id,)
        )
        
        cursor = await db.execute(
            'SELECT wins, losses, draws, total_battles FROM pvp_stats WHERE user_id = ?',
            (user_id,)
        )
        result = await cursor.fetchone()
        await db.commit()
        return result if result else (0, 0, 0, 0)


async def update_pvp_stats(winner_id, loser_id, is_draw=False):
    """PvP statistikasini yangilash"""
    async with aiosqlite.connect(DB_PATH) as db:
        if is_draw:
            # Durang
            await db.execute(
                'UPDATE pvp_stats SET draws = draws + 1, total_battles = total_battles + 1 WHERE user_id = ?',
                (winner_id,)
            )
            await db.execute(
                'UPDATE pvp_stats SET draws = draws + 1, total_battles = total_battles + 1 WHERE user_id = ?',
                (loser_id,)
            )
        else:
            # G'olib
            await db.execute(
                'UPDATE pvp_stats SET wins = wins + 1, total_battles = total_battles + 1 WHERE user_id = ?',
                (winner_id,)
            )
            # Mag'lub
            await db.execute(
                'UPDATE pvp_stats SET losses = losses + 1, total_battles = total_battles + 1 WHERE user_id = ?',
                (loser_id,)
            )
        
        await db.commit()


async def save_pvp_battle(player1_id, player2_id, player1_score, player2_score, winner_id):
    """PvP jangni tarixga saqlash"""
    async with aiosqlite.connect(DB_PATH) as db:
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        await db.execute('''
            INSERT INTO pvp_history 
            (player1_id, player2_id, player1_score, player2_score, winner_id, battle_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (player1_id, player2_id, player1_score, player2_score, winner_id, now))
        
        await db.commit()


async def get_pvp_leaderboard(limit=10):
    """PvP top o'yinchilar"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT u.username, p.wins, p.losses, p.draws, p.total_battles,
                   (p.wins * 100.0 / NULLIF(p.total_battles, 0)) as win_rate
            FROM pvp_stats p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.total_battles > 0
            ORDER BY p.wins DESC, win_rate DESC
            LIMIT ?
        ''', (limit,))
        return await cursor.fetchall()

# ==================== ADMIN - PVP STATISTIKA ====================

async def get_admin_pvp_stats():
    """Admin uchun umumiy PvP statistika"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Jami janglar
        cursor = await db.execute('SELECT COUNT(*) FROM pvp_history')
        total_battles = (await cursor.fetchone())[0]
        
        # Jami ishtirokchilar
        cursor = await db.execute('SELECT COUNT(*) FROM pvp_stats WHERE total_battles > 0')
        total_players = (await cursor.fetchone())[0]
        
        # O'rtacha jang soni
        if total_players > 0:
            avg_battles = total_battles / total_players
        else:
            avg_battles = 0
        
        # Eng faol o'yinchi
        cursor = await db.execute('''
            SELECT u.username, p.total_battles
            FROM pvp_stats p
            JOIN users u ON p.user_id = u.user_id
            ORDER BY p.total_battles DESC
            LIMIT 1
        ''')
        most_active = await cursor.fetchone()
        
        # Eng kuchli o'yinchi (eng ko'p g'alaba)
        cursor = await db.execute('''
            SELECT u.username, p.wins, p.total_battles
            FROM pvp_stats p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.total_battles > 0
            ORDER BY p.wins DESC, p.total_battles DESC
            LIMIT 1
        ''')
        strongest_player = await cursor.fetchone()
        
        return {
            'total_battles': total_battles,
            'total_players': total_players,
            'avg_battles': avg_battles,
            'most_active': most_active,
            'strongest': strongest_player
        }


async def get_pvp_recent_battles(limit=10):
    """Oxirgi PvP janglar"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT 
                u1.username as player1_name,
                u2.username as player2_name,
                h.player1_score,
                h.player2_score,
                u3.username as winner_name,
                h.battle_date
            FROM pvp_history h
            JOIN users u1 ON h.player1_id = u1.user_id
            JOIN users u2 ON h.player2_id = u2.user_id
            LEFT JOIN users u3 ON h.winner_id = u3.user_id
            ORDER BY h.id DESC
            LIMIT ?
        ''', (limit,))
        return await cursor.fetchall()


# ==================== PVP STATISTIKA MENYUSI ====================

@bot.message_handler(func=lambda m: m.text == "⚔️ PvP Statistika" and m.from_user.id == ADMIN_ID)
def admin_pvp_stats_menu(message):
    """PvP statistika menyusi"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📊 Umumiy PvP Ma'lumot", "🏆 Top PvP O'yinchilar")
    markup.row("📜 Oxirgi Janglar", "📈 PvP Tahlil")
    markup.row("🔙 Admin Panelga")
    
    bot.send_message(
        message.chat.id,
        "⚔️ PVP STATISTIKA\n\n"
        "Kerakli bo'limni tanlang:",
        reply_markup=markup
    )


# ==================== UMUMIY PVP MALUMOT ====================

@bot.message_handler(func=lambda m: m.text == "📊 Umumiy PvP Ma'lumot" and m.from_user.id == ADMIN_ID)
def show_admin_pvp_overview(message):
    """Umumiy PvP ma'lumot"""
    bot.send_message(message.chat.id, "⏳ Ma'lumot yuklanmoqda...")
    
    stats = asyncio.run(get_admin_pvp_stats())
    
    text = "📊 UMUMIY PVP MA'LUMOT\n"
    text += "━━━━━━━━━━━━━━━━━━━\n\n"
    text += f"⚔️ Jami janglar: {stats['total_battles']}\n"
    text += f"👥 Jami ishtirokchilar: {stats['total_players']}\n"
    text += f"📊 O'rtacha janglar: {stats['avg_battles']:.1f} ta\n\n"
    
    if stats['most_active']:
        name, battles = stats['most_active']
        text += f"🔥 Eng faol: @{name if name else 'Anonim'} ({battles} jang)\n"
    
    if stats['strongest']:
        name, wins, total = stats['strongest']
        win_rate = (wins / total * 100) if total > 0 else 0
        text += f"💪 Eng kuchli: @{name if name else 'Anonim'} ({wins}/{total} - {win_rate:.1f}%)\n"
    
    bot.send_message(message.chat.id, text)


# ==================== TOP PVP OYINCHILAR ====================

@bot.message_handler(func=lambda m: m.text == "🏆 Top PvP O'yinchilar" and m.from_user.id == ADMIN_ID)
def show_admin_pvp_top(message):
    """Top PvP o'yinchilar"""
    leaderboard = asyncio.run(get_pvp_leaderboard(20))
    
    if not leaderboard:
        bot.send_message(message.chat.id, "❌ Hali PvP o'yinlar yo'q!")
        return
    
    text = "🏆 TOP 20 PVP O'YINCHILAR\n"
    text += "━━━━━━━━━━━━━━━━━━━\n\n"
    
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    
    for i, (username, wins, losses, draws, total, win_rate) in enumerate(leaderboard, 1):
        medal = medals.get(i, f"{i}.")
        user_display = f"@{username}" if username else "Anonim"
        
        text += f"{medal} {user_display}\n"
        text += f"   🏆 {wins} | ❌ {losses} | 🤝 {draws}\n"
        text += f"   📊 {total} jang | 📈 {win_rate:.1f}%\n\n"
    
    # Xabarni bo'laklarga ajratish
    if len(text) > 4000:
        parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for part in parts:
            bot.send_message(message.chat.id, part)
    else:
        bot.send_message(message.chat.id, text)


# ==================== OXIRGI JANGLAR ====================

@bot.message_handler(func=lambda m: m.text == "📜 Oxirgi Janglar" and m.from_user.id == ADMIN_ID)
def show_recent_battles(message):
    """Oxirgi janglar"""
    battles = asyncio.run(get_pvp_recent_battles(15))
    
    if not battles:
        bot.send_message(message.chat.id, "❌ Hali janglar yo'q!")
        return
    
    text = "📜 OXIRGI 15 TA JANG\n"
    text += "━━━━━━━━━━━━━━━━━━━\n\n"
    
    for i, (p1, p2, s1, s2, winner, date) in enumerate(battles, 1):
        p1_name = f"@{p1}" if p1 else "Anonim"
        p2_name = f"@{p2}" if p2 else "Anonim"
        winner_name = f"@{winner}" if winner else "Durang"
        
        text += f"{i}. {p1_name} vs {p2_name}\n"
        text += f"   Natija: {s1}-{s2}\n"
        text += f"   G'olib: {winner_name}\n"
        text += f"   📅 {date[:16]}\n\n"
    
    # Xabarni bo'laklarga ajratish
    if len(text) > 4000:
        parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for part in parts:
            bot.send_message(message.chat.id, part)
    else:
        bot.send_message(message.chat.id, text)


# ==================== PVP TAHLIL ====================

@bot.message_handler(func=lambda m: m.text == "📈 PvP Tahlil" and m.from_user.id == ADMIN_ID)
def show_pvp_analytics(message):
    """PvP tahlil"""
    bot.send_message(message.chat.id, "⏳ Tahlil tayyorlanmoqda...")
    
    stats = asyncio.run(get_admin_pvp_stats())
    leaderboard = asyncio.run(get_pvp_leaderboard(100))
    
    if not leaderboard:
        bot.send_message(message.chat.id, "❌ Tahlil uchun ma'lumot yo'q!")
        return
    
    # Tahlil
    total_wins = sum([w for _, w, _, _, _, _ in leaderboard])
    total_draws = sum([d for _, _, _, d, _, _ in leaderboard])
    
    draw_rate = (total_draws / stats['total_battles'] * 100) if stats['total_battles'] > 0 else 0
    
    # O'rtacha g'alaba foizi
    avg_win_rate = sum([wr for _, _, _, _, _, wr in leaderboard]) / len(leaderboard) if leaderboard else 0
    
    text = "📈 PVP TAHLIL\n"
    text += "━━━━━━━━━━━━━━━━━━━\n\n"
    text += f"⚔️ Jami janglar: {stats['total_battles']}\n"
    text += f"👥 Faol o'yinchilar: {stats['total_players']}\n"
    text += f"📊 O'rtacha janglar: {stats['avg_battles']:.1f}\n\n"
    text += f"🎯 Durang foizi: {draw_rate:.1f}%\n"
    text += f"📈 O'rtacha g'alaba foizi: {avg_win_rate:.1f}%\n\n"
    
    # Faollik darajasi
    if stats['avg_battles'] < 2:
        activity = "📉 Past"
    elif stats['avg_battles'] < 5:
        activity = "📊 O'rtacha"
    else:
        activity = "📈 Yuqori"
    
    text += f"🔥 Faollik darajasi: {activity}\n"
    
    bot.send_message(message.chat.id, text)


# ==================== ORQAGA TUGMASI ====================

@bot.message_handler(func=lambda m: m.text == "🔙 Admin Panelga" and m.from_user.id == ADMIN_ID)
def back_to_admin_from_pvp_stats(message):
    """Admin panelga qaytish"""
    admin_panel(message)

# ==================== MAJBURIY OBUNA FUNKSIYASI ====================

def check_user_subscription(user_id):
    """Foydalanuvchi barcha kanallarga obuna ekanini tekshirish"""
    if not FORCE_SUB_ENABLED:
        return True, []
    
    not_subscribed = []
    
    for channel in FORCE_SUB_CHANNELS:
        try:
            member = bot.get_chat_member(channel['username'], user_id)
            if member.status in ['left', 'kicked']:
                not_subscribed.append(channel)
        except Exception as e:
            print(f"Kanal tekshirishda xato ({channel['username']}): {e}")
            not_subscribed.append(channel)
    
    return len(not_subscribed) == 0, not_subscribed


def create_subscription_keyboard(not_subscribed_channels, callback_data="check_sub"):
    """Obuna tugmalarini yaratish"""
    markup = types.InlineKeyboardMarkup()
    
    for channel in not_subscribed_channels:
        markup.add(
            types.InlineKeyboardButton(
                f"📢 {channel['name']}",
                url=f"https://t.me/{channel['username'][1:]}"
            )
        )
    
    markup.add(
        types.InlineKeyboardButton(
            "✅ Obuna bo'ldim, tekshirish",
            callback_data=callback_data
        )
    )
    
    return markup


# ==================== DATABASE FUNKSIYASI ====================
# Bu funksiyani database bo'limiga qo'shing

async def get_all_user_ids():
    """Barcha foydalanuvchilar ID larini olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT user_id FROM users')
        users = await cursor.fetchall()
        return [user[0] for user in users]


async def check_user_exists(user_id):
    """Foydalanuvchi mavjudligini tekshirish"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        result = await cursor.fetchone()
        return result is not None
  
async def get_random_questions(count=10):
    """Tasodifiy savollar olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT * FROM questions ORDER BY RANDOM() LIMIT ?', (count,))
        return await cursor.fetchall()


async def get_questions_count():
    """Bazadagi savollar sonini olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT COUNT(*) FROM questions')
        result = await cursor.fetchone()
        return result[0]


async def add_question(question, opt_a, opt_b, opt_c, opt_d, correct, explanation):
    """Yangi savol qo'shish"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO questions (question, option_a, option_b, option_c, option_d, correct_answer, explanation)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (question, opt_a, opt_b, opt_c, opt_d, correct, explanation))
        await db.commit()


# Kanal post funksiyalari

def send_daily_leaderboard():
    """Har kuni top foydalanuvchilar"""
    try:
        top_users = asyncio.run(get_top_users_by_level(10))
        
        if not top_users:
            print("⚠️ Top foydalanuvchilar yo'q")
            return
        
        # Bugungi sana
        today = datetime.now().strftime("%d.%m.%Y")
        
        text = f"🏆 TOP 10 FOYDALANUVCHILAR\n"
        text += f"📅 {today}\n\n"
        text += "Eng yuqori darajadagilar:\n\n"
        
        medals = ["🥇", "🥈", "🥉"]
        
        for i, (username, level, xp) in enumerate(top_users, 1):
            medal = medals[i-1] if i <= 3 else f"{i}."
            user_display = f"@{username}" if username else "Anonim"
            level_name = get_level_name(level)
            
            text += f"{medal} {user_display}\n"
            text += f"   {level_name}\n"
            text += f"   ⭐ {xp} XP\n\n"
        
        text += "━━━━━━━━━━━━━━━\n"
        text += "💡 Siz ham top 10 ga kirmoqchimisiz?\n"
        text += "🤖 Bot: @MatematikaQuizchiBot"
        
        bot.send_message(CHANNEL_USERNAME, text)
        print(f"✅ Kunlik top yuborildi: {today}")
        
    except Exception as e:
        print(f"❌ Kunlik top yuborishda xato: {e}")


def send_weekly_season_top():
    """Har hafta mavsum top"""
    try:
        season_info = asyncio.run(get_season_info())
        season_num, season_name, start_date, is_active = season_info
        
        top_users = asyncio.run(get_season_top_users(10))
        
        if not top_users:
            print("⚠️ Mavsum statistikasi yo'q")
            return
        
        today = datetime.now().strftime("%d.%m.%Y")
        
        text = f"👑 {season_name.upper()}\n"
        text += f"📅 {today}\n\n"
        text += "TOP 10 (To'g'ri javoblar):\n\n"
        
        medals = ["🥇", "🥈", "🥉"]
        
        for i, (username, correct, wrong, quizzes, accuracy) in enumerate(top_users, 1):
            medal = medals[i-1] if i <= 3 else f"{i}."
            user_display = f"@{username}" if username else "Anonim"
            
            text += f"{medal} {user_display}\n"
            text += f"   ✅ {correct} to'g'ri | 🎯 {quizzes} quiz\n\n"
        
        text += "━━━━━━━━━━━━━━━\n"
        text += "💡 Siz ham g'olib bo'lmoqchimisiz?\n"
        text += "🤖 Bot: @MatematikaQuizchiBot"
        
        bot.send_message(CHANNEL_USERNAME, text)
        print(f"✅ Haftalik mavsum top yuborildi: {today}")
        
    except Exception as e:
        print(f"❌ Haftalik top yuborishda xato: {e}")


def schedule_checker():
    """Vaqtni tekshirish (pytz siz)"""
    while True:
        try:
            now = datetime.now()
            current_hour = now.hour
            current_minute = now.minute
            current_day = now.weekday()  # 0=Dushanba, 6=Yakshanba
            
            # HAR KUNI soat 20:00 da
            if current_hour == 20 and current_minute == 0:
                send_daily_leaderboard()
                threading.Event().wait(60)
            
            # HAR YAKSHANBA soat 19:00 da
            if current_day == 6 and current_hour == 19 and current_minute == 0:
                send_weekly_season_top()
                threading.Event().wait(60)
            
            # Har 30 soniyada tekshirish
            threading.Event().wait(30)
            
        except Exception as e:
            print(f"❌ Schedule xatosi: {e}")
            threading.Event().wait(60)


def start_scheduler():
    """Schedulerni ishga tushirish"""
    scheduler_thread = threading.Thread(target=schedule_checker, daemon=True)
    scheduler_thread.start()
    print("⏰ Kanal post tizimi ishga tushdi!")
    print(f"📅 Kunlik top: har kuni 20:00 da")
    print(f"📅 Haftalik top: har yakshanba 19:00 da")


# ==================== HANDLERS ====================

# ==================== REFERAL HANDLERS ====================
# Bu handlerlarni message_handler bo'limiga qo'shing (start_command dan keyin)

@bot.message_handler(func=lambda m: m.text == "👥 Referal")
def show_referral_menu(message):
    """Referal menyusi"""
    user_id = message.from_user.id
    ref_count, bonus = asyncio.run(get_referral_stats(user_id))
    
    ref_link = f"https://t.me/{bot.get_me().username}?start=ref_{user_id}"
    
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("📊 Top Referalchilar", callback_data="top_referrals"))
    
    bot.send_message(
        message.chat.id,
        f"👥 Referal tizimi\n\n"
        f"🔗 Sizning referal havolangiz:\n"
        f"`{ref_link}`\n\n"
        f"📊 Sizning statistikangiz:\n"
        f"👤 Taklif qilganlar: {ref_count} kishi\n"
        f"⭐ Bonus ballar: {bonus}\n\n"
        f"💡 Har bir do'stingiz uchun 5 ball oling!\n"
        f"📱 Havolani do'stlaringizga yuboring va ball yig'ing!",
        parse_mode='Markdown',
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == "top_referrals")
def show_leaderboard(call):
    """Top referalchilarni ko'rsatish"""
    leaderboard = asyncio.run(get_referral_leaderboard(10))
    
    if not leaderboard:
        bot.answer_callback_query(call.id, "❌ Hali referal yo'q!")
        return
    
    text = "🏆 Top 10 Referalchilar\n\n"
    
    medals = ["🥇", "🥈", "🥉"]
    for i, (username, ref_count, bonus) in enumerate(leaderboard, 1):
        medal = medals[i-1] if i <= 3 else f"{i}."
        text += f"{medal} @{username if username else 'Anonim'}\n"
        text += f"   👥 {ref_count} kishi | ⭐ {bonus} ball\n\n"
    
    bot.send_message(call.message.chat.id, text)


# ==================== 5-QISM: PROFIL HANDLERLAR ====================
# Joylashtirish: Sozlamalar handlerlaridan keyin (850-qator atrofiga)

@bot.message_handler(func=lambda m: m.text == "👤 Profil")
def show_profile(message):
    """Profil ko'rsatish"""
    user_id = message.from_user.id
    asyncio.run(show_user_profile(message.chat.id, user_id))


# ==================== SOZLAMALAR BO'LIMI ====================

@bot.message_handler(func=lambda m: m.text == "⚙️ Sozlamalar")
def settings_menu(message):
    """Sozlamalar bo'limi"""
    user_id = message.from_user.id
    reminder_enabled, reminder_time, streak, best_streak = asyncio.run(get_reminder_settings(user_id))
    avatar, custom_title, color, bio, topics_read = asyncio.run(get_profile_settings(user_id))

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎨 Avatar Emoji o'zgartirish", callback_data="edit_avatar"))
    markup.add(types.InlineKeyboardButton("📝 Bio o'zgartirish", callback_data="edit_bio"))
    markup.add(types.InlineKeyboardButton("🔙 Bosh menyu", callback_data="settings_back_main"))

    status_emoji = "✅" if reminder_enabled else "❌"
    bio_text = bio if bio else "Yo'q"
    title_text = custom_title if custom_title else "Yo'q"

    bot.send_message(
        message.chat.id,
        f"⚙️ SOZLAMALAR\n\n"
        f"👤 Profil:\n"
        f"  {avatar} Avatar: {avatar}\n"
        f"  🏅 Unvon: {title_text}\n"
        f"  📝 Bio: {bio_text}\n\n"
        f"🔥 Streak: {streak} kun (🏆 Eng yaxshi: {best_streak})\n\n"
        f"Quyidagi sozlamalardan birini tanlang:",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == "settings_back_main")
def settings_back_main(call):
    """Sozlamalardan bosh menyuga qaytish"""
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "🏠 Bosh menyu")
    start_command(call.message)


async def show_user_profile(chat_id, user_id):
    """Foydalanuvchi profilini ko'rsatish"""
    # Ma'lumotlarni yig'ish
    try:
        user = bot.get_chat(user_id)
        username = f"@{user.username}" if user.username else user.first_name
    except Exception:
        # DB dan username olish
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute('SELECT username FROM users WHERE user_id = ?', (user_id,))
            row = await cursor.fetchone()
            username = f"@{row[0]}" if row and row[0] else f"ID:{user_id}"
    
    # Statistika
    correct, wrong, total_quizzes = await get_user_stats(user_id)
    level, xp = await get_user_level_info(user_id)
    level_name = get_level_name(level)
    next_xp = get_next_level_xp(level)
    
    # Streak
    _, _, streak, best_streak = await get_reminder_settings(user_id)
    
    # Clan
    user_clan = await get_user_clan(user_id)
    clan_text = f"🛡️ {user_clan[1]} (#{user_clan[2]})" if user_clan else "❌ Yo'q"
    
    # PvP
    pvp_wins, pvp_losses, pvp_draws, pvp_total = await get_pvp_stats(user_id)
    pvp_winrate = (pvp_wins / pvp_total * 100) if pvp_total > 0 else 0
    
    # Tezkor Quiz
    speed_games, speed_best_time, speed_best_score, _ = await get_speed_quiz_stats(user_id)
    
    # Referal
    referal_count, _ = await get_referral_stats(user_id)
    
    # Profil sozlamalari
    avatar, custom_title, color, bio, topics_read = await get_profile_settings(user_id)
    
    # Yutuqlar
    achievements = await get_user_achievements(user_id)
    achievement_count = len(achievements)
    total_achievements = len(ACHIEVEMENTS)
    
    # Progress bar
    if next_xp:
        current_level_min = LEVELS[level]['min']
        level_xp = xp - current_level_min
        level_max = next_xp - current_level_min
        progress = int((level_xp / level_max) * 10)
        progress_bar = "█" * progress + "░" * (10 - progress)
        progress_text = f"[{progress_bar}] {level_xp}/{level_max}"
    else:
        progress_text = "MAX LEVEL"
    
    # Aniqlik
    total_answers = correct + wrong
    accuracy = (correct / total_answers * 100) if total_answers > 0 else 0
    
    # Title
    display_title = custom_title if custom_title else level_name
    
    # Profil matni
    text = (
        f"{avatar} {username}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🎖 Daraja: {level} • {display_title}\n"
        f"⭐ XP: {xp:,}\n"
        f"📊 {progress_text}\n"
        f"🔥 Streak: {streak} kun (🏆 {best_streak})\n"
        f"🛡️ Clan: {clan_text}\n\n"
        f"🏆 YUTUQLAR: {achievement_count}/{total_achievements}\n"
    )
    
    # Eng so'nggi 6 ta yutuq
    if achievements:
        text += "━━━━━━━━━━━━━━━━━━━\n"
        recent = achievements[-6:]
        for ach_id, _ in recent:
            if ach_id in ACHIEVEMENTS:
                ach = ACHIEVEMENTS[ach_id]
                text += f"{ach['emoji']} "
        text += "\n\n"
    else:
        text += "Hali yutuq yo'q\n\n"
    
    text += (
        f"📊 STATISTIKA\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 Quiz: {total_quizzes} | ✅ {correct} | ❌ {wrong}\n"
        f"📈 Aniqlik: {accuracy:.1f}%\n"
        f"⚔️ PvP: {pvp_wins}-{pvp_losses} ({pvp_winrate:.0f}%)\n"
        f"⚡ Tezkor: {speed_games} o'yin | 🏆 {speed_best_score}\n"
        f"👥 Referal: {referal_count}\n"
        f"📚 O'qigan: {topics_read} mavzu"
    )
    
    # Tugmalar
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🏆 Yutuqlar", callback_data=f"show_achievements_{user_id}"),
        types.InlineKeyboardButton("⚙️ Sozlash", callback_data="edit_profile")
    )
    
    bot.send_message(chat_id, text, reply_markup=markup)


# ==================== 6-QISM: BOSHQANING PROFILINI KO'RISH ====================

search_sessions = {}  # Profil qidirish uchun alohida sessiya

@bot.message_handler(func=lambda m: m.text == "🔍 Profil Qidirish")
def search_profile_start(message):
    """Boshqaning profilini qidirish"""
    search_sessions[message.from_user.id] = {'step': 1}
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("❌ Bekor qilish")
    
    bot.send_message(
        message.chat.id,
        "🔍 PROFIL QIDIRISH\n\n"
        "Foydalanuvchi ID sini kiriting:\n"
        "(Masalan: 123456789)\n\n"
        "💡 ID ni bilish uchun: @userinfobot",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.from_user.id in search_sessions)
def search_profile_process(message):
    """Profil qidirish jarayoni"""
    user_id = message.from_user.id
    
    if message.text == "❌ Bekor qilish":
        del search_sessions[user_id]
        start_command(message)
        return
    
    try:
        target_id = int(message.text.strip())
        
        # Avval DB da mavjudligini tekshirish
        user_exists = asyncio.run(check_user_exists(target_id))
        
        if not user_exists:
            bot.send_message(
                message.chat.id,
                "❌ Bu ID bilan foydalanuvchi topilmadi!\n"
                "Foydalanuvchi botdan foydalanmagan bo'lishi mumkin.\n\n"
                "Boshqa ID kiriting yoki ❌ Bekor qilish tugmasini bosing."
            )
            return
        
        asyncio.run(show_user_profile(message.chat.id, target_id))
        del search_sessions[user_id]
        
    except ValueError:
        bot.send_message(
            message.chat.id,
            "❌ Noto'g'ri format!\n\n"
            "Faqat raqam kiriting (masalan: 123456789)"
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Xatolik yuz berdi: {str(e)}\n\nQaytadan urinib ko'ring."
        )


# ==================== 7-QISM: YUTUQLARNI KO'RISH ====================

@bot.callback_query_handler(func=lambda call: call.data.startswith('show_achievements_'))
def show_achievements(call):
    """Yutuqlarni ko'rsatish"""
    target_id = int(call.data.split('_')[2])
    
    achievements = asyncio.run(get_user_achievements(target_id))
    
    # Kategoriyalarga ajratish
    categories = {
        'Quiz': ['first_quiz', 'quiz_master_10', 'quiz_master_50', 'quiz_master_100', 'perfect_quiz'],
        'Streak': ['streak_3', 'streak_7', 'streak_30'],
        'PvP': ['pvp_first_win', 'pvp_champion', 'pvp_legend'],
        'Clan': ['clan_founder', 'clan_hero'],
        'Referal': ['ambassador', 'influencer'],
        'Daraja': ['level_5', 'level_7'],
        'XP': ['xp_1000', 'xp_5000', 'xp_10000'],
        'Boshqa': ['speed_master', 'reader']
    }
    
    unlocked_ids = [ach[0] for ach in achievements]
    
    text = "🏆 YUTUQLAR\n"
    text += f"{len(unlocked_ids)}/{len(ACHIEVEMENTS)}\n"
    text += "━━━━━━━━━━━━━━━━━━━\n\n"
    
    for category, ach_ids in categories.items():
        text += f"📁 {category}:\n"
        for ach_id in ach_ids:
            if ach_id in ACHIEVEMENTS:
                ach = ACHIEVEMENTS[ach_id]
                if ach_id in unlocked_ids:
                    text += f"✅ {ach['emoji']} {ach['name']}\n"
                else:
                    text += f"🔒 ??? ({ach['description']})\n"
        text += "\n"
    
    # Xabarni bo'laklarga ajratish
    if len(text) > 4000:
        parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for part in parts:
            bot.send_message(call.message.chat.id, part)
    else:
        bot.send_message(call.message.chat.id, text)


# ==================== 8-QISM: PROFIL SOZLASH ====================

@bot.callback_query_handler(func=lambda call: call.data == "edit_profile")
def edit_profile_menu(call):
    """Profil sozlash menyusi"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎨 Avatar Emoji", callback_data="edit_avatar"))
    markup.add(types.InlineKeyboardButton("📝 Bio", callback_data="edit_bio"))
    markup.add(types.InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_profile"))
    
    bot.send_message(
        call.message.chat.id,
        "⚙️ PROFIL SOZLASH\n\n"
        "Nima o'zgartirmoqchisiz?",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == "edit_avatar")
def edit_avatar_start(call):
    """Avatar o'zgartirish"""
    admin_sessions[call.from_user.id] = {'type': 'edit_avatar'}
    
    bot.send_message(
        call.message.chat.id,
        "🎨 AVATAR EMOJI\n\n"
        "Bitta emoji yuboring:\n"
        "(Masalan: 😎, 🚀, 🔥, 💎, 👑)"
    )


@bot.message_handler(func=lambda m: m.from_user.id in admin_sessions and 
                     admin_sessions[m.from_user.id].get('type') == 'edit_avatar')
def edit_avatar_process(message):
    """Avatar o'zgartirish jarayoni"""
    user_id = message.from_user.id
    
    # Emoji ekanini tekshirish (oddiy tekshirish)
    if len(message.text) <= 2 and message.text:
        asyncio.run(update_profile_settings(user_id, avatar_emoji=message.text))
        bot.send_message(
            message.chat.id,
            f"✅ Avatar o'zgartirildi: {message.text}"
        )
        del admin_sessions[user_id]
    else:
        bot.send_message(
            message.chat.id,
            "❌ Faqat bitta emoji yuboring!"
        )


@bot.callback_query_handler(func=lambda call: call.data == "edit_bio")
def edit_bio_start(call):
    """Bio o'zgartirish"""
    admin_sessions[call.from_user.id] = {'type': 'edit_bio'}
    
    bot.send_message(
        call.message.chat.id,
        "📝 BIO\n\n"
        "O'zingiz haqingizda qisqacha yozing:\n"
        "(Max: 100 belgi)"
    )


@bot.message_handler(func=lambda m: m.from_user.id in admin_sessions and 
                     admin_sessions[m.from_user.id].get('type') == 'edit_bio')
def edit_bio_process(message):
    """Bio o'zgartirish jarayoni"""
    user_id = message.from_user.id
    bio = message.text
    
    if len(bio) <= 100:
        asyncio.run(update_profile_settings(user_id, bio=bio))
        bot.send_message(
            message.chat.id,
            f"✅ Bio saqlandi:\n{bio}"
        )
        del admin_sessions[user_id]
    else:
        bot.send_message(
            message.chat.id,
            "❌ Juda uzun! Max 100 belgi."
        )


@bot.callback_query_handler(func=lambda call: call.data == "back_to_profile")
def back_to_profile(call):
    """Profilga qaytish"""
    asyncio.run(show_user_profile(call.message.chat.id, call.from_user.id))



# ==================== GURUH QUIZ COMMANDLARI ====================
# Joylashtirish: Handler bo'limiga (1000-qator atrofiga)

@bot.message_handler(commands=['quiz', 'test', 'quizboshlash'])
def start_group_quiz_command(message):
    """Guruh quizni boshlash (command)"""
    # Faqat guruh uchun
    if message.chat.type not in ['group', 'supergroup']:
        bot.reply_to(message, "❌ Bu buyruq faqat guruhlarda ishlaydi!")
        return
    
    group_id = message.chat.id
    
    # Allaqachon faol quiz bormi?
    if group_id in group_quiz_sessions:
        bot.reply_to(message, "⚠️ Quiz allaqachon boshlangan! Tugashini kuting.")
        return
    
    # Savollar mavjudligini tekshirish
    questions = asyncio.run(get_random_questions(10))
    
    if len(questions) < 10:
        bot.reply_to(
            message,
            "❌ Savollar yetarli emas!\n"
            f"Hozir bazada {len(questions)} ta savol bor.\n"
            "Kamida 10 ta savol kerak."
        )
        return
    
    # Sessiya yaratish
    group_quiz_sessions[group_id] = {
        'questions': questions,
        'current': 0,
        'participants': {},  # {user_id: {'name': name, 'score': score}}
        'admin_id': message.from_user.id,
        'message_ids': []
    }
    
    # Boshlash xabari
    start_text = (
        "🎮 GURUH QUIZ BOSHLANDI!\n\n"
        "📝 10 ta savol\n"
        "⚡ Har savol uchun 4 ta variant\n"
        "🏆 Eng ko'p to'g'ri javob bergan g'olib!\n\n"
        "Tayyor bo'ling... 3️⃣ 2️⃣ 1️⃣"
    )
    
    msg = bot.send_message(group_id, start_text)
    group_quiz_sessions[group_id]['message_ids'].append(msg.message_id)
    
    # 3 soniya kutish
    import time
    time.sleep(3)
    
    # Birinchi savolni yuborish
    send_group_question(group_id)


# ==================== QUIZNI YAKUNLASH ====================

def finish_group_quiz(group_id):
    """Guruh quizni yakunlash"""
    if group_id not in group_quiz_sessions:
        return
    
    session = group_quiz_sessions[group_id]
    participants = session['participants']
    
    if not participants:
        bot.send_message(
            group_id,
            "😕 Hech kim ishtirok etmadi!\n"
            "Keyingi safar qatnashing! 📚"
        )
        del group_quiz_sessions[group_id]
        return
    
    # Natijalarni saralash
    sorted_participants = sorted(
        participants.items(),
        key=lambda x: x[1]['score'],
        reverse=True
    )
    
    # G'olib
    winner_id, winner_data = sorted_participants[0]
    winner_score = winner_data['score']
    winner_name = winner_data['name']
    
    # Top 10
    top_count = min(10, len(sorted_participants))
    
    # Natija xabari
    result_text = (
        "🏆 GURUH QUIZ YAKUNLANDI!\n\n"
        f"👥 Ishtirokchilar: {len(participants)}\n"
        f"📝 Savollar: 10 ta\n\n"
        f"👑 G'OLIB:\n"
        f"{winner_name} - {winner_score}/10 ✅\n\n"
        f"📊 TOP {top_count}:\n"
        "━━━━━━━━━━━━━━━━━━━\n"
    )
    
    medals = {0: "🥇", 1: "🥈", 2: "🥉"}
    
    for i, (user_id, data) in enumerate(sorted_participants[:top_count]):
        medal = medals.get(i, f"{i+1}.")
        result_text += f"{medal} {data['name']} - {data['score']}/10\n"
    
    result_text += "\n💡 Keyingi quizda qatnashing! /quiz"
    
    bot.send_message(group_id, result_text)
    
    # Statistikani saqlash (har bir ishtirokchi uchun)
    for user_id, data in participants.items():
        asyncio.run(update_group_quiz_stats(user_id, group_id, data['score']))
    
    # Tarixga saqlash
    asyncio.run(save_group_quiz_history(
        group_id,
        len(participants),
        winner_id,
        winner_score
    ))
    
    # Sessiyani o'chirish
    del group_quiz_sessions[group_id]


# ==================== GURUH REYTINGI ====================

@bot.message_handler(commands=['topleaderboard', 'top'])
def show_group_leaderboard(message):
    """Guruh reytingi"""
    if message.chat.type not in ['group', 'supergroup']:
        bot.reply_to(message, "❌ Bu buyruq faqat guruhlarda ishlaydi!")
        return
    
    group_id = message.chat.id
    
    leaderboard = asyncio.run(get_group_leaderboard(group_id, 10))
    
    if not leaderboard:
        bot.send_message(
            group_id,
            "📊 GURUH REYTINGI\n\n"
            "❌ Hali statistika yo'q!\n"
            "/quiz buyrug'i bilan quiz boshlang!"
        )
        return
    
    text = "📊 GURUH REYTINGI\n"
    text += "Top 10 o'yinchilar\n"
    text += "━━━━━━━━━━━━━━━━━━━\n\n"
    
    medals = {0: "🥇", 1: "🥈", 2: "🥉"}
    
    for i, (user_id, games, best_score, total_score) in enumerate(leaderboard):
        try:
            user = bot.get_chat_member(group_id, user_id).user
            name = user.first_name
        except:
            name = "Anonim"
        
        medal = medals.get(i, f"{i+1}.")
        text += f"{medal} {name}\n"
        text += f"   🏆 Eng yaxshi: {best_score}/10\n"
        text += f"   🎮 O'yinlar: {games}\n\n"
    
    bot.send_message(group_id, text)


# ==================== QUIZNI BEKOR QILISH ====================

@bot.message_handler(commands=['stopquiz', 'bekorqilish'])
def stop_group_quiz(message):
    """Quizni bekor qilish (faqat admin)"""
    if message.chat.type not in ['group', 'supergroup']:
        return
    
    group_id = message.chat.id
    
    if group_id not in group_quiz_sessions:
        bot.reply_to(message, "❌ Hozir faol quiz yo'q!")
        return
    
    # Admin tekshirish
    user_id = message.from_user.id
    
    try:
        chat_member = bot.get_chat_member(group_id, user_id)
        is_admin = chat_member.status in ['creator', 'administrator']
    except:
        is_admin = False
    
    session = group_quiz_sessions[group_id]
    
    if not is_admin and user_id != session['admin_id']:
        bot.reply_to(message, "❌ Faqat admin yoki quiz boshlagan odam bekor qilishi mumkin!")
        return
    
    # Sessiyani o'chirish
    del group_quiz_sessions[group_id]
    
    bot.send_message(
        group_id,
        "❌ Quiz bekor qilindi!\n"
        "Yangi quiz boshlash uchun: /quiz"
    )


# ==================== YORDAM ====================

@bot.message_handler(commands=['quizhelp', 'yordam'])
def quiz_help(message):
    """Guruh quiz yordami"""
    if message.chat.type not in ['group', 'supergroup']:
        return
    
    help_text = (
        "📚 GURUH QUIZ YO'RIQNOMASI\n\n"
        "🎮 ASOSIY BUYRUQLAR:\n"
        "/quiz - Quizni boshlash\n"
        "/next - Keyingi savolga o'tish\n"
        "/top - Guruh reytingi\n"
        "/stopquiz - Quizni bekor qilish\n\n"
        "❓ QANDAY O'YNALADI:\n"
        "1. Admin yoki a'zo /quiz yozadi\n"
        "2. Bot 10 ta savol beradi\n"
        "3. Har kim inline tugmalar orqali javob beradi\n"
        "4. Har savoldan keyin /next buyrug'i bilan keyingi savol\n"
        "5. Oxirida top 10 ko'rsatiladi\n\n"
        "💡 MASLAHAT:\n"
        "• Tez javob bering!\n"
        "• Har savolda faqat 1 marta javob beriladi\n"
        "• G'olib eng ko'p to'g'ri javob bergan bo'ladi\n\n"
        "🏆 Omad!"
    )
    
    bot.send_message(message.chat.id, help_text)


# ==================== 5-QISM: TEZKOR QUIZ HANDLERLAR ====================
# Joylashtirish: Handler bo'limiga (300-400 qator atrofiga)

@bot.message_handler(func=lambda m: m.text == "⚡ Tezkor Quiz")

def speed_quiz_menu(message):
    """Tezkor quiz menyusi"""
    user_id = message.from_user.id
    
    # Statistikani olish
    games, best_time, best_score, total_score = asyncio.run(get_speed_quiz_stats(user_id))
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🚀 Boshlash", "📊 Mening Statistikam")
    markup.row("🏆 Reytingi", "🔙 Orqaga")
    
    bot.send_message(
        message.chat.id,
        f"⚡ TEZKOR QUIZ\n\n"
        f"📝 5 ta savol\n"
        f"⏱ 30 soniya (har savol uchun 6 soniya)\n"
        f"🎯 Tez javob = ko'proq ball!\n\n"
        f"Sizning statistikangiz:\n"
        f"🎮 O'yinlar: {games}\n"
        f"⏱ Eng yaxshi vaqt: {best_time}s\n"
        f"🏆 Eng yaxshi ball: {best_score}\n"
        f"📊 Jami ball: {total_score}\n\n"
        f"Tayyor bo'lsangiz boshlang!",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text == "🚀 Boshlash")
def start_speed_quiz(message):
    """Tezkor quizni boshlash"""
    user_id = message.from_user.id
    
    # 5 ta tasodifiy savol olish
    questions = asyncio.run(get_random_questions(5))
    
    if len(questions) < 5:
        bot.send_message(message.chat.id, "❌ Savollar yetarli emas! (Kamida 5 ta savol kerak)")
        return
    
    import time
    
    # Sessiya yaratish
    speed_quiz_sessions[user_id] = {
        'questions': questions,
        'current': 0,
        'score': 0,
        'start_time': time.time(),
        'question_times': []
    }
    
    bot.send_message(
        message.chat.id,
        "⚡ TEZKOR QUIZ BOSHLANDI!\n\n"
        "⏱ Har savol uchun 6 soniya!\n"
        "🚀 Tez javob bering!\n"
        "💎 Tez javob = ko'proq ball!\n\n"
        "Tayyor bo'ling..."
    )
    
    time.sleep(1)
    send_speed_question(message.chat.id, user_id)


def send_speed_question(chat_id, user_id):
    """Tezkor quiz savolini yuborish"""
    import time
    
    if user_id not in speed_quiz_sessions:
        return
    
    session = speed_quiz_sessions[user_id]
    
    # Barcha savollar tugadi mi?
    if session['current'] >= len(session['questions']):
        finish_speed_quiz(chat_id, user_id)
        return
    
    question_data = session['questions'][session['current']]
    q_id, question, opt_a, opt_b, opt_c, opt_d, correct, explanation = question_data
    
    # Savol boshlangan vaqtni saqlash
    session['question_times'].append(time.time())
    
    # Inline tugmalar
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(f"A", callback_data=f"speed_{user_id}_{session['current']}_A"),
        types.InlineKeyboardButton(f"B", callback_data=f"speed_{user_id}_{session['current']}_B"),
        types.InlineKeyboardButton(f"C", callback_data=f"speed_{user_id}_{session['current']}_C"),
        types.InlineKeyboardButton(f"D", callback_data=f"speed_{user_id}_{session['current']}_D")
    )
    
    current_num = session['current'] + 1
    
    bot.send_message(
        chat_id,
        f"⚡ Savol {current_num}/5 | ⏱ 6 soniya!\n\n"
        f"{question}\n\n"
        f"A) {opt_a}\n"
        f"B) {opt_b}\n"
        f"C) {opt_c}\n"
        f"D) {opt_d}",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('speed_'))
def speed_quiz_answer(call):
    """Tezkor quiz javobini qayta ishlash"""
    import time
    
    parts = call.data.split('_')
    user_id = int(parts[1])
    question_index = int(parts[2])
    user_answer = parts[3]
    
    # Foydalanuvchi o'zining o'yinini o'ynayotganini tekshirish
    if call.from_user.id != user_id:
        bot.answer_callback_query(call.id, "❌ Bu sizning o'yiningiz emas!")
        return
    
    # Sessiya mavjudligini tekshirish
    if user_id not in speed_quiz_sessions:
        bot.answer_callback_query(call.id, "❌ O'yin tugagan!")
        return
    
    session = speed_quiz_sessions[user_id]
    
    # Vaqtni tekshirish
    if session['current'] >= len(session['question_times']):
        bot.answer_callback_query(call.id, "❌ Xato!")
        return
    
    question_start_time = session['question_times'][session['current']]
    time_taken = time.time() - question_start_time
    
    # 6 soniyadan oshdi mi?
    if time_taken > 6:
        bot.answer_callback_query(call.id, "⏱ Vaqt tugadi!", show_alert=True)
        bot.send_message(
            call.message.chat.id,
            f"⏱ Vaqt tugadi!\n"
            f"Siz {time_taken:.1f} soniya sarfladingiz (max: 6s)"
        )
        session['current'] += 1
        time.sleep(0.5)
        send_speed_question(call.message.chat.id, user_id)
        return
    
    # Javobni tekshirish
    question_data = session['questions'][question_index]
    correct_answer = question_data[6]
    
    if user_answer == correct_answer:
        # TO'G'RI JAVOB
        # Ball hisoblash: tez javob = ko'proq ball
        # 0-2 soniya: 20 ball
        # 2-4 soniya: 15 ball
        # 4-6 soniya: 10 ball
        if time_taken <= 2:
            points = 20
        elif time_taken <= 4:
            points = 15
        else:
            points = 10
        
        session['score'] += points
        
        bot.answer_callback_query(call.id, f"✅ To'g'ri! +{points} ball")
        bot.send_message(
            call.message.chat.id,
            f"✅ TO'G'RI JAVOB!\n"
            f"⚡ +{points} ball\n"
            f"⏱ Vaqt: {time_taken:.1f}s"
        )
    else:
        # NOTO'G'RI JAVOB
        bot.answer_callback_query(call.id, f"❌ Noto'g'ri! To'g'ri: {correct_answer}", show_alert=True)
        bot.send_message(
            call.message.chat.id,
            f"❌ Noto'g'ri javob!\n"
            f"✅ To'g'ri javob: {correct_answer}"
        )
    
    # Keyingi savolga o'tish
    session['current'] += 1
    time.sleep(0.5)
    send_speed_question(call.message.chat.id, user_id)


def finish_speed_quiz(chat_id, user_id):
    """Tezkor quizni yakunlash"""
    import time
    
    if user_id not in speed_quiz_sessions:
        return
    
    session = speed_quiz_sessions[user_id]
    
    # Umumiy vaqt va ball
    total_time = int(time.time() - session['start_time'])
    score = session['score']
    
    # Statistikani yangilash
    new_time_record, new_score_record = asyncio.run(update_speed_quiz_stats(user_id, total_time, score))
    
    # Natija xabari
    result_text = (
        f"⚡ TEZKOR QUIZ YAKUNLANDI!\n\n"
        f"🏆 To'plagan ball: {score}/100\n"
        f"⏱ Umumiy vaqt: {total_time}s\n\n"
    )
    
    # Rekordlar
    if new_time_record:
        result_text += "🎉 YANGI VAQT REKORDI!\n"
    if new_score_record:
        result_text += "🎉 YANGI BALL REKORDI!\n"
    
    # XP berish
    xp_gained = score * 2  # Har ball uchun 2 XP
    new_level, new_xp, level_up = asyncio.run(update_user_xp(user_id, xp_gained))
    
    # Clan XP (agar clanda bo'lsa)
    asyncio.run(update_clan_xp(user_id, xp_gained))
    
    result_text += f"\n⭐ +{xp_gained} XP olindi!"
    
    # Baho
    if score >= 90:
        result_text += "\n\n🏆 AJOYIB! Siz tezlik ustasisiz!"
    elif score >= 70:
        result_text += "\n\n👍 YAXSHI! Ko'p mashq qiling!"
    elif score >= 50:
        result_text += "\n\n📚 O'RTACHA! Tezlikni oshiring!"
    else:
        result_text += "\n\n💪 Davom eting! Mashq qiling!"
    
    bot.send_message(chat_id, result_text)
    
    # Level up xabari
    if level_up:
        level_name = get_level_name(new_level)
        bot.send_message(
            chat_id,
            f"🎉 YANGI DARAJA!\n\n"
            f"{level_name}\n"
            f"🆙 Daraja: {new_level}\n"
            f"⭐ XP: {new_xp}"
        )
    
    # Sessiyani o'chirish
    del speed_quiz_sessions[user_id]


@bot.message_handler(func=lambda m: m.text == "📊 Mening Statistikam")
def show_speed_stats(message):
    """Tezkor quiz statistika"""
    user_id = message.from_user.id
    
    games, best_time, best_score, total_score = asyncio.run(get_speed_quiz_stats(user_id))
    
    if games == 0:
        bot.send_message(
            message.chat.id,
            "❌ Hali tezkor quiz o'ynamadingiz!\n\n"
            "🚀 Boshlash tugmasini bosing va o'ynab ko'ring!"
        )
        return
    
    # O'rtacha ball
    avg_score = total_score / games if games > 0 else 0
    
    # O'rtacha vaqt (taxminiy)
    avg_time = best_time + 5  # Taxminiy
    
    bot.send_message(
        message.chat.id,
        f"📊 TEZKOR QUIZ STATISTIKANGIZ\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎮 O'ynagan o'yinlar: {games}\n"
        f"⏱ Eng yaxshi vaqt: {best_time}s\n"
        f"🏆 Eng yaxshi ball: {best_score}\n"
        f"📊 Jami ball: {total_score}\n"
        f"📈 O'rtacha ball: {avg_score:.1f}\n\n"
        f"💡 Tez javob berish uchun mashq qiling!"
    )


@bot.message_handler(func=lambda m: m.text == "🏆 Reytingi")
def show_speed_leaderboard(message):
    """Tezkor quiz reytingi"""
    leaderboard = asyncio.run(get_speed_quiz_leaderboard(10))
    
    if not leaderboard:
        bot.send_message(message.chat.id, "❌ Hali hech kim o'ynamagan!")
        return
    
    text = "🏆 TEZKOR QUIZ REYTINGI\n"
    text += "Top 10 o'yinchilar\n"
    text += "━━━━━━━━━━━━━━━━━━━\n\n"
    
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    
    for i, (username, score, time_val, games) in enumerate(leaderboard, 1):
        medal = medals.get(i, f"{i}.")
        user_display = f"@{username}" if username else "Anonim"
        
        text += f"{medal} {user_display}\n"
        text += f"   🏆 {score} ball | ⏱ {time_val}s\n"
        text += f"   🎮 {games} o'yin\n\n"
    
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: m.text == "🔙 Orqaga")
def back_from_speed_quiz(message):
    """Tezkor quizdan orqaga"""
    start_command(message)


# ==================== 5-QISM: CLAN HANDLERLAR ====================
# Joylashtirish: Tezkor quiz handlerlaridan keyin (500-qator atrofiga)

@bot.message_handler(func=lambda m: m.text == "🛡 Clan")

def clan_menu(message):
    """Clan menyusi"""
    user_id = message.from_user.id
    
    user_clan = asyncio.run(get_user_clan(user_id))
    
    if user_clan:
        # Clanda
        show_clan_dashboard(message, user_clan)
    else:
        # Clanda emas
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("➕ Clan Yaratish", "🔍 Clan Qidirish")
        markup.row("🏆 Clan Reytingi", "🔙 Orqaga")
        
        bot.send_message(
            message.chat.id,
            "🛡 CLAN TIZIMI\n\n"
            "Siz hali biror clanga a'zo emassiz!\n\n"
            "➕ Yangi clan yarating\n"
            "🔍 Mavjud clanga qo'shiling\n"
            "🏆 Clan reytingini ko'ring\n\n"
            "Kerakli bo'limni tanlang:",
            reply_markup=markup
        )


def show_clan_dashboard(message, clan_data):
    """Clan dashboard"""
    clan_id, name, tag, description, total_xp, member_count, role, max_members = clan_data
    
    # Role emoji
    role_emoji = {"leader": "👑", "elder": "⭐", "member": "👤"}.get(role, "👤")
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("👥 A'zolar", "📊 Clan Statistika")
    markup.row("📤 Taklif Havolasi", "🚪 Clanmdan chiqish")
    
    if role == "leader":
        markup.row("⚙️ Clan Sozlamalari")
    
    markup.row("🔙 Orqaga")
    
    bot.send_message(
        message.chat.id,
        f"🛡 {name}\n"
        f"🏷 Tag: #{tag}\n"
        f"📝 {description or 'Tavsif yoq'}\n\n"
        f"⭐ Jami XP: {total_xp:,}\n"
        f"👥 A'zolar: {member_count}/{max_members}\n"
        f"{role_emoji} Sizning rolingiz: {role}\n\n"
        f"Kerakli bo'limni tanlang:",
        reply_markup=markup
    )


# ==================== CLAN YARATISH ====================

@bot.message_handler(func=lambda m: m.text == "➕ Clan Yaratish")
def create_clan_start(message):
    """Clan yaratish boshlash"""
    user_id = message.from_user.id

    # 💎 LEVEL VA XP TEKSHIRUVI (premium emas, level kerak!)
    can, msg = asyncio.run(check_clan_create_eligibility(user_id))
    if not can:
        req = CLAN_CREATE_REQUIREMENTS
        bot.send_message(
            message.chat.id,
            f"🛡 KLAN YARATISH TALABLARI\n\n"
            f"Klan yaratish uchun:\n"
            f"  📊 Kamida {req['min_level']}-daraja kerak\n"
            f"  💰 {req['xp_cost']:,} XP sarflanadi\n\n"
            f"{msg}\n\n"
            f"💡 Ko'proq quiz yeching va darajangizni oshiring! 🚀"
        )
        return

    # Allaqachon clanda ekanini tekshirish
    user_clan = asyncio.run(get_user_clan(user_id))

    if user_clan:
        bot.send_message(
            message.chat.id,
            "❌ Siz allaqachon clan a'zosisiz!\n"
            "Avval clandangizdan chiqing."
        )
        return

    # XP ni ayirish (klan yaratish narxi)
    asyncio.run(deduct_clan_xp(user_id))
    bot.send_message(message.chat.id,
        f"💰 Klan yaratish uchun {CLAN_CREATE_REQUIREMENTS['xp_cost']:,} XP sarflandi!")

    admin_sessions[user_id] = {'type': 'create_clan', 'step': 1}
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("❌ Bekor qilish")
    
    bot.send_message(
        message.chat.id,
        "➕ CLAN YARATISH\n\n"
        "1️⃣ Clan nomini kiriting:\n"
        "(3-30 belgi, masalan: Matematika Pro)\n\n"
        "❌ Bekor qilish uchun tugmani bosing",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.from_user.id in admin_sessions and 
                     admin_sessions[m.from_user.id].get('type') == 'create_clan')
def create_clan_process(message):
    """Clan yaratish jarayoni"""
    user_id = message.from_user.id
    session = admin_sessions[user_id]
    
    if message.text == "❌ Bekor qilish":
        del admin_sessions[user_id]
        clan_menu(message)
        return
    
    if session['step'] == 1:
        # Clan nomi
        name = message.text
        
        if len(name) < 3 or len(name) > 30:
            bot.send_message(message.chat.id, "❌ Nom 3-30 belgi orasida bo'lishi kerak!")
            return
        
        session['name'] = name
        session['step'] = 2
        
        bot.send_message(
            message.chat.id,
            "2️⃣ Clan TAG ini kiriting:\n"
            "(2-6 belgi, faqat harflar va raqamlar)\n"
            "(Masalan: MP123)\n\n"
            "Bu tag clan identifikatori bo'ladi."
        )
    
    elif session['step'] == 2:
        # Clan TAG
        tag = message.text.upper()
        
        if len(tag) < 2 or len(tag) > 6:
            bot.send_message(message.chat.id, "❌ TAG 2-6 belgi orasida bo'lishi kerak!")
            return
        
        if not tag.isalnum():
            bot.send_message(message.chat.id, "❌ TAG faqat harflar va raqamlardan iborat bo'lishi kerak!")
            return
        
        # TAG mavjudligini tekshirish
        existing = asyncio.run(get_clan_by_tag(tag))
        if existing:
            bot.send_message(message.chat.id, f"❌ #{tag} TAG band! Boshqa TAG kiriting.")
            return
        
        session['tag'] = tag
        session['step'] = 3
        
        bot.send_message(
            message.chat.id,
            "3️⃣ Clan tavsifini kiriting:\n"
            "(10-100 belgi)\n\n"
            "Clanni qisqacha tavsiflang."
        )
    
    elif session['step'] == 3:
        # Tavsif
        description = message.text
        
        if len(description) < 10 or len(description) > 100:
            bot.send_message(message.chat.id, "❌ Tavsif 10-100 belgi orasida bo'lishi kerak!")
            return
        
        session['description'] = description
        
        # Tasdiqlash
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("✅ Yaratish", callback_data="create_clan_confirm"),
            types.InlineKeyboardButton("❌ Bekor qilish", callback_data="create_clan_cancel")
        )
        
        bot.send_message(
            message.chat.id,
            f"🛡 CLAN KO'RINISHI:\n\n"
            f"📛 Nom: {session['name']}\n"
            f"🏷 TAG: #{session['tag']}\n"
            f"📝 Tavsif: {session['description']}\n\n"
            f"Clanni yaratamizmi?",
            reply_markup=markup
        )


@bot.callback_query_handler(func=lambda call: call.data == "create_clan_confirm")
def create_clan_confirm(call):
    """Clan yaratishni tasdiqlash"""
    user_id = call.from_user.id
    
    if user_id not in admin_sessions:
        bot.answer_callback_query(call.id, "❌ Sessiya tugagan!")
        return
    
    session = admin_sessions[user_id]
    
    # Clan yaratish
    success, result = asyncio.run(create_clan(
        session['name'],
        session['tag'],
        session['description'],
        user_id
    ))
    
    if success:
        bot.answer_callback_query(call.id, "✅ Clan yaratildi!")
        bot.send_message(
            call.message.chat.id,
            f"🎉 CLAN YARATILDI!\n\n"
            f"🛡 {session['name']}\n"
            f"🏷 TAG: #{session['tag']}\n\n"
            f"Siz clan liderisiz! 👑\n"
            f"Do'stlaringizni taklif qiling!"
        )
        
        del admin_sessions[user_id]
        
        # Clan menyusini ko'rsatish
        user_clan = asyncio.run(get_user_clan(user_id))
        show_clan_dashboard(call.message, user_clan)
    else:
        bot.answer_callback_query(call.id, f"❌ Xato: {result}", show_alert=True)


@bot.callback_query_handler(func=lambda call: call.data == "create_clan_cancel")
def create_clan_cancel(call):
    """Clan yaratishni bekor qilish"""
    user_id = call.from_user.id
    
    if user_id in admin_sessions:
        del admin_sessions[user_id]
    
    bot.answer_callback_query(call.id, "❌ Bekor qilindi")
    bot.send_message(call.message.chat.id, "❌ Clan yaratish bekor qilindi.")
    clan_menu(call.message)


# ==================== CLAN QIDIRISH ====================

@bot.message_handler(func=lambda m: m.text == "🔍 Clan Qidirish")
def search_clan_start(message):
    """Clan qidirish boshlash"""
    user_id = message.from_user.id
    
    # Allaqachon clanda ekanini tekshirish
    user_clan = asyncio.run(get_user_clan(user_id))
    
    if user_clan:
        bot.send_message(
            message.chat.id,
            "❌ Siz allaqachon clan a'zosisiz!\n"
            "Avval clandangizdan chiqing."
        )
        return
    
    admin_sessions[user_id] = {'type': 'search_clan', 'step': 1}
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("❌ Bekor qilish")
    
    bot.send_message(
        message.chat.id,
        "🔍 CLAN QIDIRISH\n\n"
        "Clan TAG ini kiriting:\n"
        "(Masalan: MP123)\n\n"
        "❌ Bekor qilish uchun tugmani bosing",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.from_user.id in admin_sessions and 
                     admin_sessions[m.from_user.id].get('type') == 'search_clan')
def search_clan_process(message):
    """Clan qidirish jarayoni"""
    user_id = message.from_user.id
    
    if message.text == "❌ Bekor qilish":
        del admin_sessions[user_id]
        clan_menu(message)
        return
    
    tag = message.text.upper()
    
    clan = asyncio.run(get_clan_by_tag(tag))
    
    if not clan:
        bot.send_message(
            message.chat.id,
            f"❌ #{tag} TAG bilan clan topilmadi!\n\n"
            "Boshqa TAG kiriting yoki bekor qiling."
        )
        return
    
    clan_id, name, tag, description, leader_id, total_xp, member_count, max_members = clan
    
    # Lider ismini olish
    leader = bot.get_chat(leader_id)
    leader_name = f"@{leader.username}" if leader.username else leader.first_name
    
    # Qo'shilish tugmasi
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Qo'shilish", callback_data=f"join_clan_{clan_id}"),
        types.InlineKeyboardButton("❌ Bekor qilish", callback_data="join_clan_cancel")
    )
    
    bot.send_message(
        message.chat.id,
        f"🛡 CLAN TOPILDI!\n\n"
        f"📛 Nom: {name}\n"
        f"🏷 TAG: #{tag}\n"
        f"📝 Tavsif: {description}\n"
        f"👑 Lider: {leader_name}\n"
        f"⭐ XP: {total_xp:,}\n"
        f"👥 A'zolar: {member_count}/{max_members}\n\n"
        f"Qo'shilmoqchimisiz?",
        reply_markup=markup
    )
    
    del admin_sessions[user_id]


@bot.callback_query_handler(func=lambda call: call.data.startswith('join_clan_'))
def join_clan_callback(call):
    """Clanga qo'shilish"""
    user_id = call.from_user.id
    
    if call.data == "join_clan_cancel":
        bot.answer_callback_query(call.id, "❌ Bekor qilindi")
        bot.send_message(call.message.chat.id, "❌ Bekor qilindi.")
        clan_menu(call.message)
        return
    
    clan_id = int(call.data.split('_')[2])
    
    success, message_text = asyncio.run(join_clan(user_id, clan_id))
    
    if success:
        bot.answer_callback_query(call.id, "✅ Qo'shildingiz!")
        
        clan = asyncio.run(get_clan_by_id(clan_id))
        bot.send_message(
            call.message.chat.id,
            f"🎉 CLANGA QO'SHILDINGIZ!\n\n"
            f"🛡 {clan[1]}\n"
            f"🏷 #{clan[2]}\n\n"
            f"Xush kelibsiz! 👋"
        )
        
        # Clan lideriga xabar
        leader_id = clan[4]
        username = call.from_user.username or call.from_user.first_name
        bot.send_message(
            leader_id,
            f"👤 Yangi a'zo qo'shildi!\n\n"
            f"@{username} clanigizga qo'shildi!"
        )
        
        # Clan menyusini ko'rsatish
        user_clan = asyncio.run(get_user_clan(user_id))
        show_clan_dashboard(call.message, user_clan)
    else:
        bot.answer_callback_query(call.id, f"❌ {message_text}", show_alert=True)


# ==================== CLAN TAKLIF ====================

def handle_clan_invite(message, clan_tag, user_id):
    """Clan taklifni qayta ishlash"""
    # Allaqachon clanda ekanini tekshirish
    user_clan = asyncio.run(get_user_clan(user_id))
    
    if user_clan:
        bot.send_message(
            message.chat.id,
            "❌ Siz allaqachon clan a'zosisiz!"
        )
        return
    
    clan = asyncio.run(get_clan_by_tag(clan_tag))
    
    if not clan:
        bot.send_message(
            message.chat.id,
            f"❌ #{clan_tag} TAG bilan clan topilmadi!"
        )
        return
    
    clan_id, name, tag, description, leader_id, total_xp, member_count, max_members = clan
    
    # Qo'shilish tugmasi
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Qo'shilish", callback_data=f"join_clan_{clan_id}"),
        types.InlineKeyboardButton("❌ Rad etish", callback_data="join_clan_cancel")
    )
    
    bot.send_message(
        message.chat.id,
        f"🛡 CLAN TAKLIFИ!\n\n"
        f"📛 {name}\n"
        f"🏷 TAG: #{tag}\n"
        f"📝 {description}\n"
        f"⭐ XP: {total_xp:,}\n"
        f"👥 A'zolar: {member_count}/{max_members}\n\n"
        f"Qo'shilmoqchimisiz?",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text == "📤 Taklif Havolasi")
def clan_invite_link(message):
    """Clan taklif havolasi"""
    user_id = message.from_user.id
    
    user_clan = asyncio.run(get_user_clan(user_id))
    
    if not user_clan:
        bot.send_message(message.chat.id, "❌ Siz clanda emassiz!")
        return
    
    clan_id, name, tag, description, total_xp, member_count, role, max_members = user_clan
    
    # Taklif havolasi
    bot_username = bot.get_me().username
    invite_link = f"https://t.me/{bot_username}?start=clan_{tag}"
    
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(
        "📤 Havolani ulashish",
        url=f"https://t.me/share/url?url={invite_link}&text=🛡 {name} claniga qo'shiling!"
    ))
    
    bot.send_message(
        message.chat.id,
        f"📤 TAKLIF HAVOLASI\n\n"
        f"🛡 {name} (#{tag})\n\n"
        f"🔗 Havola:\n"
        f"`{invite_link}`\n\n"
        f"Do'stlaringizga yuboring!",
        parse_mode='Markdown',
        reply_markup=markup
    )


# ==================== CLAN AZOLAR ====================

@bot.message_handler(func=lambda m: m.text == "👥 A'zolar")
def show_clan_members(message):
    """Clan a'zolari ro'yxati"""
    user_id = message.from_user.id
    
    user_clan = asyncio.run(get_user_clan(user_id))
    
    if not user_clan:
        bot.send_message(message.chat.id, "❌ Siz clanda emassiz!")
        return
    
    clan_id = user_clan[0]
    members = asyncio.run(get_clan_members(clan_id))
    
    if not members:
        bot.send_message(message.chat.id, "❌ A'zolar topilmadi!")
        return
    
    text = f"👥 CLAN A'ZOLARI\n"
    text += f"Jami: {len(members)}\n"
    text += "━━━━━━━━━━━━━━━━━━━\n\n"
    
    role_emoji = {"leader": "👑", "elder": "⭐", "member": "👤"}
    
    for member_id, username, role, contribution, level, xp in members:
        emoji = role_emoji.get(role, "👤")
        user_display = f"@{username}" if username else "Anonim"
        level_name = get_level_name(level)
        
        text += f"{emoji} {user_display}\n"
        text += f"   {level_name}\n"
        text += f"   💎 Hissa: {contribution:,} XP\n\n"
    
    # Xabarni bo'laklarga ajratish
    if len(text) > 4000:
        parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for part in parts:
            bot.send_message(message.chat.id, part)
    else:
        bot.send_message(message.chat.id, text)


# ==================== CLAN STATISTIKA ====================

@bot.message_handler(func=lambda m: m.text == "📊 Clan Statistika")
def show_clan_stats(message):
    """Clan statistikasi"""
    user_id = message.from_user.id
    
    user_clan = asyncio.run(get_user_clan(user_id))
    
    if not user_clan:
        bot.send_message(message.chat.id, "❌ Siz clanda emassiz!")
        return
    
    clan_id, name, tag, description, total_xp, member_count, role, max_members = user_clan
    members = asyncio.run(get_clan_members(clan_id))
    
    # Statistika hisoblash
    total_contribution = sum([m[3] for m in members])
    avg_contribution = total_contribution / member_count if member_count > 0 else 0
    
    # Top 3 contributor
    top_contributors = sorted(members, key=lambda x: x[3], reverse=True)[:3]
    
    text = f"📊 CLAN STATISTIKA\n"
    text += f"🛡 {name} (#{tag})\n"
    text += "━━━━━━━━━━━━━━━━━━━\n\n"
    text += f"⭐ Jami XP: {total_xp:,}\n"
    text += f"👥 A'zolar: {member_count}/{max_members}\n"
    text += f"📈 O'rtacha hissa: {avg_contribution:,.0f} XP\n\n"
    text += "🏆 TOP 3 HISSA:\n\n"
    
    medals = {0: "🥇", 1: "🥈", 2: "🥉"}
    
    for i, (member_id, username, role, contribution, level, xp) in enumerate(top_contributors):
        medal = medals.get(i, "")
        user_display = f"@{username}" if username else "Anonim"
        text += f"{medal} {user_display}\n"
        text += f"   💎 {contribution:,} XP\n\n"
    
    bot.send_message(message.chat.id, text)


# ==================== CLAN REYTINGI ====================

@bot.message_handler(func=lambda m: m.text == "🏆 Clan Reytingi")
def show_clan_leaderboard(message):
    """Clan reytingi"""
    leaderboard = asyncio.run(get_clan_leaderboard(10))
    
    if not leaderboard:
        bot.send_message(message.chat.id, "❌ Hali clanlar yo'q!")
        return
    
    text = "🏆 CLAN REYTINGI\n"
    text += "Top 10 Clanlar\n"
    text += "━━━━━━━━━━━━━━━━━━━\n\n"
    
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    
    for i, (name, tag, xp, members) in enumerate(leaderboard, 1):
        medal = medals.get(i, f"{i}.")
        
        text += f"{medal} {name}\n"
        text += f"   🏷 #{tag}\n"
        text += f"   ⭐ {xp:,} XP | 👥 {members} a'zo\n\n"
    
    bot.send_message(message.chat.id, text)


# ==================== CLANNAN CHIQISH ====================

@bot.message_handler(func=lambda m: m.text == "🚪 Clanmdan chiqish")
def leave_clan_confirm(message):
    """Clannan chiqish tasdiqlash"""
    user_id = message.from_user.id
    
    user_clan = asyncio.run(get_user_clan(user_id))
    
    if not user_clan:
        bot.send_message(message.chat.id, "❌ Siz clanda emassiz!")
        return
    
    clan_id, name, tag, description, total_xp, member_count, role, max_members = user_clan
    
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Ha, chiqish", callback_data="leave_clan_yes"),
        types.InlineKeyboardButton("❌ Yo'q", callback_data="leave_clan_no")
    )
    
    warning = ""
    if role == "leader" and member_count > 1:
        warning = "\n\n⚠️ Siz lider! Avval liderlikni o'tkazing yoki barcha a'zolarni chiqarib yuboring."
    elif role == "leader":
        warning = "\n\n⚠️ Siz chiqsangiz clan o'chib ketadi!"
    
    bot.send_message(
        message.chat.id,
        f"⚠️ TASDIQLASH\n\n"
        f"🛡 {name} (#{tag}) clanidan chiqmoqchimisiz?"
        f"{warning}\n\n"
        f"Davom etasizmi?",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == "leave_clan_yes")
def leave_clan_yes(call):
    """Clannan chiqish"""
    user_id = call.from_user.id
    
    success, message_text = asyncio.run(leave_clan(user_id))
    
    if success:
        bot.answer_callback_query(call.id, "✅ Chiqildi")
        bot.send_message(
            call.message.chat.id,
            f"✅ {message_text}\n\n"
            "Yangi clanga qo'shilishingiz yoki o'zingizning clanigizni yaratishingiz mumkin."
        )
        clan_menu(call.message)
    else:
        bot.answer_callback_query(call.id, f"❌ {message_text}", show_alert=True)


@bot.callback_query_handler(func=lambda call: call.data == "leave_clan_no")
def leave_clan_no(call):
    """Clannan chiqishni bekor qilish"""
    bot.answer_callback_query(call.id, "❌ Bekor qilindi")
    bot.send_message(call.message.chat.id, "❌ Bekor qilindi.")


# ==================== CLAN SOZLAMALARI (LIDER UCHUN) ====================

@bot.message_handler(func=lambda m: m.text == "⚙️ Clan Sozlamalari")
def clan_settings(message):
    """Clan sozlamalari (faqat lider)"""
    user_id = message.from_user.id
    
    user_clan = asyncio.run(get_user_clan(user_id))
    
    if not user_clan:
        bot.send_message(message.chat.id, "❌ Siz clanda emassiz!")
        return
    
    role = user_clan[6]
    
    if role != "leader":
        bot.send_message(message.chat.id, "❌ Faqat lider sozlaydi!")
        return
    
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🗑 A'zoni chiqarish", "📝 Tavsifni o'zgartirish")
    markup.row("🔙 Clan Menyusiga")
    
    bot.send_message(
        message.chat.id,
        "⚙️ CLAN SOZLAMALARI\n\n"
        "Kerakli bo'limni tanlang:",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text == "🗑 A'zoni chiqarish")
def kick_member_start(message):
    """A'zoni chiqarish boshlash"""
    user_id = message.from_user.id
    
    user_clan = asyncio.run(get_user_clan(user_id))
    
    if not user_clan:
        bot.send_message(message.chat.id, "❌ Siz clanda emassiz!")
        return
    
    role = user_clan[6]
    
    if role != "leader":
        bot.send_message(message.chat.id, "❌ Faqat lider chiqarishi mumkin!")
        return
    
    clan_id = user_clan[0]
    members = asyncio.run(get_clan_members(clan_id))
    
    # Liderdan tashqari a'zolar
    members = [m for m in members if m[2] != 'leader']
    
    if not members:
        bot.send_message(message.chat.id, "❌ Chiqariladigan a'zo yo'q!")
        return
    
    # Inline tugmalar
    markup = types.InlineKeyboardMarkup()
    
    for member_id, username, role, contribution, level, xp in members:
        user_display = f"@{username}" if username else f"ID: {member_id}"
        markup.add(
            types.InlineKeyboardButton(
                f"🗑 {user_display}",
                callback_data=f"kick_{member_id}"
            )
        )
    
    markup.add(types.InlineKeyboardButton("❌ Bekor qilish", callback_data="kick_cancel"))
    
    bot.send_message(
        message.chat.id,
        "🗑 A'ZONI CHIQARISH\n\n"
        "Chiqarmoqchi bo'lgan a'zoni tanlang:",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('kick_'))
def kick_member_callback(call):
    """A'zoni chiqarish callback"""
    if call.data == "kick_cancel":
        bot.answer_callback_query(call.id, "❌ Bekor qilindi")
        bot.send_message(call.message.chat.id, "❌ Bekor qilindi.")
        return
    
    leader_id = call.from_user.id
    member_id = int(call.data.split('_')[1])
    
    # Clan ID ni olish
    user_clan = asyncio.run(get_user_clan(leader_id))
    clan_id = user_clan[0]
    
    # A'zoni chiqarish
    asyncio.run(kick_member(clan_id, member_id))
    
    # A'zoga xabar
    try:
        bot.send_message(
            member_id,
            f"⚠️ Siz {user_clan[1]} clanidan chiqarib yubordingiz!"
        )
    except:
        pass
    
    bot.answer_callback_query(call.id, "✅ Chiqarib yuborildi!")
    bot.send_message(call.message.chat.id, "✅ A'zo chiqarib yuborildi!")


# ==================== ORQAGA TUGMALARI ====================

@bot.message_handler(func=lambda m: m.text == "🔙 Clan Menyusiga")
def back_to_clan_dashboard(message):
    """Clan menyusiga qaytish"""
    user_id = message.from_user.id
    user_clan = asyncio.run(get_user_clan(user_id))
    
    if user_clan:
        show_clan_dashboard(message, user_clan)
    else:
        clan_menu(message)


@bot.message_handler(func=lambda m: m.text == "🔙 Orqaga")
def back_from_clan(message):
    """Clannan orqaga"""
    start_command(message)
    
    
# ==================== FOYDALANUVCHI UCHUN START COMMAND ====================


# ==================== START COMMAND BILAN MAJBURIY OBUNA ====================
# start_command funksiyasini yangilang


@bot.message_handler(commands=['start'])
def start_command(message):
    """Start buyrug'i - majburiy obuna bilan"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    # MAJBURIY OBUNANI TEKSHIRISH
    is_subscribed, not_subscribed = check_user_subscription(user_id)
    
    if not is_subscribed:
        # Obuna bo'lmagan
        channel_list = "\n".join([f"📢 {ch['name']}" for ch in not_subscribed])
        
        markup = create_subscription_keyboard(not_subscribed)
        
        bot.send_message(
            message.chat.id,
            f"🔒 Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:\n\n"
            f"{channel_list}\n\n"
            f"Obuna bo'lgandan so'ng '✅ Obuna bo'ldim' tugmasini bosing.",
            reply_markup=markup
        )
        return
    
    # Obuna bo'lgan - davom etish
    asyncio.run(add_user(user_id, username))
    asyncio.run(init_referral_table())
    
    # Referal/PvP tekshirish
    if ' ' in message.text:
        ref_param = message.text.split()[1]
        
        # BU QISMNI QO'SHING (pvp dan oldin):
        if ref_param.startswith('clan_'):
            clan_tag = ref_param.split('_')[1]
            handle_clan_invite(message, clan_tag, user_id)
            return
        
        if ref_param.startswith('pvp_'):
            inviter_id = int(ref_param.split('_')[1])
            if inviter_id != user_id:
                handle_pvp_invite(message, inviter_id, user_id)
                return
        
        elif ref_param.startswith('ref_'):
            referrer_id = int(ref_param.split('_')[1])
            if referrer_id != user_id:
                asyncio.run(add_referral(user_id, referrer_id))
                bot.send_message(
                    referrer_id,
                    f"🎉 @{username} sizning havolangiz orqali botga qo'shildi!\n"
                    f"⭐ Sizga 5 bonus ball berildi!"
                )
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🎯 Quizni boshlash", "👤 Profil")
    markup.row("⚔️ PvP Battle", "⚡ Tezkor Quiz")
    markup.row("📚 O'rganish", "👥 Referal")
    markup.row("🛡 Clan", "⚙️ Sozlamalar")
    markup.row("🏆 Turnir", "💎 Premium")
    markup.row("🔍 Profil Qidirish")
    
    if user_id == ADMIN_ID:
        markup.row("⚙️ Admin Panel")
    
    bot.send_message(
        message.chat.id,
        f"🎓 Assalomu alaykum, {username}!\n\n"
        "Matematika quiz botiga xush kelibsiz!\n\n"
        "🎯 Quiz - 10 ta savol\n"
        "📚 O'rganish - nazariya\n"
        "⚡ Tezkor Quiz - 5 savol, 30 soniya!\n"
        "👥 Referal - do'stlarni taklif qiling\n"
        "⚔️ PvP Battle - do'stingiz bilan raqobatlashing!\n\n"
         "🛡 Clan - jamoa yarating!\n"
        "Boshlash uchun tugmani bosing! 👇",
        reply_markup=markup
    )

# ==================== OBUNA TEKSHIRISH CALLBACK ====================

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription_callback(call):
    """Obuna tekshirish tugmasi"""
    user_id = call.from_user.id
    
    is_subscribed, not_subscribed = check_user_subscription(user_id)
    
    if not is_subscribed:
        # Hali obuna bo'lmagan
        channel_list = "\n".join([f"📢 {ch['name']}" for ch in not_subscribed])
        
        bot.answer_callback_query(
            call.id,
            f"❌ Hali obuna bo'lmadingiz!\n\n{channel_list}",
            show_alert=True
        )
    else:
        # Obuna bo'lgan
        bot.answer_callback_query(call.id, "✅ Obuna tasdiqlandi!")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        
        # Start commandni qayta chaqirish
        start_command(call.message)



@bot.message_handler(func=lambda m: m.text == "🎯 Quizni boshlash")
def start_quiz(message):
    """Quiz boshlash"""
    user_id = message.from_user.id

    # 💎 PREMIUM LIMIT TEKSHIRUVI
    if not check_and_start_quiz(message):
        return

    asyncio.run(init_quiz_session(user_id))
    
    bot.send_message(
        message.chat.id,
        "⏳ Quiz tayyorlanmoqda...\n\nSavollar yuklanmoqda... iltimos kuting!"
    )
    
    asyncio.run(send_next_question(message.chat.id, user_id))


async def init_quiz_session(user_id):
    """Quiz sessiyasini boshlash"""
    questions = await get_random_questions(10)
    
    if len(questions) < 10:
        return False
    
    user_sessions[user_id] = {
        'questions': questions,
        'current': 0,
        'correct': 0,
        'wrong': 0
    }
    return True


async def send_next_question(chat_id, user_id):
    """Keyingi savolni yuborish"""
    if user_id not in user_sessions:
        bot.send_message(chat_id, "❌ Xatolik yuz berdi. /start buyrug'ini qayta bosing.")
        return
    
    session = user_sessions[user_id]
    
    if session['current'] >= len(session['questions']):
        await finish_quiz(chat_id, user_id)
        return
    
    question_data = session['questions'][session['current']]
    q_id, question, opt_a, opt_b, opt_c, opt_d, correct, explanation = question_data
    
    current_num = session['current'] + 1
    total = len(session['questions'])
    
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(f"A) {opt_a}", callback_data=f"ans_A_{q_id}"),
        types.InlineKeyboardButton(f"B) {opt_b}", callback_data=f"ans_B_{q_id}")
    )
    markup.row(
        types.InlineKeyboardButton(f"C) {opt_c}", callback_data=f"ans_C_{q_id}"),
        types.InlineKeyboardButton(f"D) {opt_d}", callback_data=f"ans_D_{q_id}")
    )
    
    bot.send_message(
        chat_id,
        f"📝 Savol {current_num}/{total}\n\n"
        f"{question}\n\n"
        f"A) {opt_a}\n"
        f"B) {opt_b}\n"
        f"C) {opt_c}\n"
        f"D) {opt_d}",
        reply_markup=markup
    )

# ==================== QUIZ TUGAGANDA YANGILASH ====================
# finish_quiz funksiyasiga qo'shing


# ==================== QUIZ TUGAGANDA XP BERISH ====================
# finish_quiz funksiyasini yangilang

async def finish_quiz(chat_id, user_id):
    """Quizni yakunlash - XP, daraja, yutuqlar bilan"""
    session = user_sessions[user_id]
    correct = session['correct']
    wrong = session['wrong']
    total = len(session['questions'])
    percentage = (correct / total) * 100
    
    # Umumiy statistika
    await update_user_stats(user_id, correct, wrong)
    
    # Mavsum statistikasi
    try:
        user_chat = bot.get_chat(user_id)
        username = user_chat.username or user_chat.first_name
    except Exception:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute('SELECT username FROM users WHERE user_id = ?', (user_id,))
            row = await cursor.fetchone()
            username = row[0] if row and row[0] else f"User{user_id}"
    await update_season_stats(user_id, username, correct, wrong)
    
    # Streak yangilash
    await update_streak(user_id)
    
    # XP VA DARAJA
    xp_gained = calculate_xp_from_quiz(correct, wrong)
    # 💎 Premium XP multiplier
    xp_multiplier = get_xp_multiplier_sync(user_id)
    xp_gained = xp_gained * xp_multiplier
    new_level, new_xp, level_up = await update_user_xp(user_id, xp_gained)
    
    # Clan XP
    await update_clan_xp(user_id, xp_gained)
    
    # Natija
    if percentage >= 80:
        emoji = "🏆"
        comment = "Ajoyib natija!"
    elif percentage >= 60:
        emoji = "👍"
        comment = "Yaxshi natija!"
    elif percentage >= 40:
        emoji = "📚"
        comment = "O'rta natija. Ko'proq mashq qiling!"
    else:
        emoji = "💪"
        comment = "Mashq qilishda davom eting!"
    
    # Asosiy xabar
    result_text = (
        f"{emoji} Quiz yakunlandi!\n\n"
        f"✅ To'g'ri javoblar: {correct}\n"
        f"❌ Noto'g'ri javoblar: {wrong}\n"
        f"📊 Natija: {percentage:.1f}%\n\n"
        f"{comment}\n\n"
        f"⭐ XP olindi: +{xp_gained}\n"
        f"📈 Jami XP: {new_xp}"
    )
    
    bot.send_message(chat_id, result_text)
    
    # Level Up xabari
    if level_up:
        level_name = get_level_name(new_level)
        next_xp = get_next_level_xp(new_level)
        
        level_up_text = (
            f"🎉 TABRIKLAYMAN!\n\n"
            f"Siz yangi darajaga chiqdingiz!\n"
            f"{level_name}\n\n"
            f"🆙 Daraja: {new_level}\n"
            f"⭐ XP: {new_xp}"
        )
        
        if next_xp:
            level_up_text += f"\n\n💎 Keyingi daraja uchun: {next_xp - new_xp} XP kerak"
        
        bot.send_message(chat_id, level_up_text)
    
    # Streak yangilash
    new_streak, streak_updated = await update_quiz_streak(user_id)
    
    if streak_updated and new_streak > 1:
        bot.send_message(
            chat_id,
            f"🔥 KETMA-KET {new_streak} KUN!\n\n"
            f"Siz {new_streak} kun ketma-ket quiz yechdingiz!\n"
            f"Davom eting! 💪"
        )
    
    # YUTUQLARNI TEKSHIRISH
    
    # 10/10 yutuq
    if correct == 10:
        if await unlock_achievement(user_id, 'perfect_quiz'):
            xp_reward = await give_achievement_reward(user_id, 'perfect_quiz')
            bot.send_message(
                chat_id,
                f"🎉 YANGI YUTUQ!\n\n"
                f"💯 Perfectionist\n"
                f"10/10 to'g'ri javob!\n\n"
                f"⭐ +{xp_reward} XP mukofot!"
            )
    
    # Barcha yutuqlarni tekshirish
    new_achievements = await check_and_unlock_achievements(user_id)
    
    for ach_id in new_achievements:
        ach = ACHIEVEMENTS[ach_id]
        xp_reward = await give_achievement_reward(user_id, ach_id)
        bot.send_message(
            chat_id,
            f"🎉 YANGI YUTUQ!\n\n"
            f"{ach['emoji']} {ach['name']}\n"
            f"{ach['description']}\n\n"
            f"⭐ +{xp_reward} XP mukofot!"
        )
    
    # Sessiyani o'chirish
    del user_sessions[user_id]
#-----------+++++++++*+*-*-*--*-*-*-*-*-*-


@bot.callback_query_handler(func=lambda call: call.data.startswith('ans_'))
def handle_answer(call):
    """Javob qayta ishlash"""
    user_id = call.from_user.id
    
    if user_id not in user_sessions:
        bot.answer_callback_query(call.id, "❌ Sessiya tugagan. Qaytadan boshlang!")
        return
    
    parts = call.data.split('_')
    user_answer = parts[1]
    question_id = int(parts[2])
    
    session = user_sessions[user_id]
    question_data = session['questions'][session['current']]
    correct_answer = question_data[6]
    explanation = question_data[7]
    
    if user_answer == correct_answer:
        session['correct'] += 1
        bot.answer_callback_query(call.id, "✅ To'g'ri javob!", show_alert=False)
        bot.send_message(call.message.chat.id, "✅ To'g'ri javob!")
    else:
        session['wrong'] += 1
        bot.answer_callback_query(call.id, f"❌ Noto'g'ri! To'g'ri javob: {correct_answer}", show_alert=True)
        
        response = f"❌ Noto'g'ri javob!\n\n✅ To'g'ri javob: {correct_answer}"
        if explanation:
            response += f"\n\n💡 Izoh: {explanation}"
        
        bot.send_message(call.message.chat.id, response)
    
    session['current'] += 1
    
    asyncio.run(send_next_question(call.message.chat.id, user_id))


# ==================== PVP MENU ====================

@bot.message_handler(func=lambda m: m.text == "⚔️ PvP Battle")
def pvp_menu(message):
    """PvP asosiy menyu"""
    user_id = message.from_user.id
    
    # Statistika olish
    wins, losses, draws, total = asyncio.run(get_pvp_stats(user_id))
    
    if total > 0:
        win_rate = (wins / total) * 100
    else:
        win_rate = 0
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("⚔️ Do'st bilan o'ynash", "📊 PvP Statistika")
    markup.row("🏆 PvP Reytingi", "🔙 Orqaga")
    
    bot.send_message(
        message.chat.id,
        f"⚔️ PvP BATTLE\n\n"
        f"Sizning PvP statistikangiz:\n"
        f"🏆 G'alabalar: {wins}\n"
        f"❌ Mag'lubiyatlar: {losses}\n"
        f"🤝 Duranglar: {draws}\n"
        f"📊 Jami janglar: {total}\n"
        f"📈 G'alaba foizi: {win_rate:.1f}%\n\n"
        f"Kerakli bo'limni tanlang:",
        reply_markup=markup
    )


# ==================== DO'ST BILAN O'YNASH ====================

@bot.message_handler(func=lambda m: m.text == "⚔️ Do'st bilan o'ynash")
def pvp_invite_menu(message):
    """Do'stni taklif qilish"""
    user_id = message.from_user.id

    # 💎 PREMIUM PvP LIMIT
    if not check_and_start_pvp(message):
        return

    username = bot.get_chat(user_id).username or bot.get_chat(user_id).first_name
    
    # PvP havola yaratish
    bot_username = bot.get_me().username
    pvp_link = f"https://t.me/{bot_username}?start=pvp_{user_id}"
    
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("📤 Havolani ulashish", url=f"https://t.me/share/url?url={pvp_link}&text=⚔️ Menga qarshi PvP Battle o'yna!"))
    
    bot.send_message(
        message.chat.id,
        f"⚔️ DO'ST BILAN O'YNASH\n\n"
        f"1️⃣ Quyidagi havolani do'stingizga yuboring\n"
        f"2️⃣ Do'stingiz havolani bosib botga kiradi\n"
        f"3️⃣ O'yin avtomatik boshlanadi!\n\n"
        f"🔗 Sizning PvP havolangiz:\n"
        f"`{pvp_link}`\n\n"
        f"⚡ Har ikkovingiz ham bir xil 5 ta savolga javob berasiz!\n"
        f"🏆 Ko'proq to'g'ri javob bergan g'olib bo'ladi!",
        parse_mode='Markdown',
        reply_markup=markup
    )


def handle_pvp_invite(message, inviter_id, invited_id):
    """PvP taklifni qabul qilish"""
    inviter_username = bot.get_chat(inviter_id).username or bot.get_chat(inviter_id).first_name
    invited_username = bot.get_chat(invited_id).username or bot.get_chat(invited_id).first_name
    
    # Taklif yaratish
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Qabul qilish", callback_data=f"pvp_accept_{inviter_id}"),
        types.InlineKeyboardButton("❌ Rad etish", callback_data=f"pvp_decline_{inviter_id}")
    )
    
    bot.send_message(
        invited_id,
        f"⚔️ PVP BATTLE TAKLIFI!\n\n"
        f"@{inviter_username} sizni PvP Battle ga taklif qildi!\n\n"
        f"📝 5 ta bir xil savol\n"
        f"⚡ Kim ko'proq to'g'ri javob bersa g'olib!\n"
        f"🏆 Reytingga ta'sir qiladi\n\n"
        f"Qabul qilasizmi?",
        reply_markup=markup
    )
    
    # Taklifni saqlash
    pvp_invites[invited_id] = inviter_id
    
    # Taklif qiluvchiga xabar
    bot.send_message(
        inviter_id,
        f"⏳ @{invited_username} ga taklif yuborildi!\n\n"
        f"Ularning javobini kutaylik..."
    )


# ==================== PVP QABUL/RAD QILISH ====================

@bot.callback_query_handler(func=lambda call: call.data.startswith('pvp_accept_'))
def pvp_accept(call):
    """PvP taklifni qabul qilish"""
    inviter_id = int(call.data.split('_')[2])
    invited_id = call.from_user.id
    
    bot.answer_callback_query(call.id, "✅ Taklif qabul qilindi!")
    
    # O'yinni boshlash
    start_pvp_battle(inviter_id, invited_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('pvp_decline_'))
def pvp_decline(call):
    """PvP taklifni rad etish"""
    inviter_id = int(call.data.split('_')[2])
    invited_id = call.from_user.id
    
    bot.answer_callback_query(call.id, "❌ Taklif rad etildi")
    
    invited_username = bot.get_chat(invited_id).username or bot.get_chat(invited_id).first_name
    
    bot.send_message(
        call.message.chat.id,
        "❌ Siz taklifni rad etdingiz."
    )
    
    bot.send_message(
        inviter_id,
        f"😔 @{invited_username} taklifingizni rad etdi."
    )
    
    if invited_id in pvp_invites:
        del pvp_invites[invited_id]


# ==================== PVP O'YIN BOSHLASH ====================

def start_pvp_battle(player1_id, player2_id):
    """PvP jangni boshlash"""
    # Bir xil 5 ta savolni olish
    questions = asyncio.run(get_random_questions(5))
    
    if len(questions) < 5:
        bot.send_message(player1_id, "❌ Savollar yetarli emas!")
        bot.send_message(player2_id, "❌ Savollar yetarli emas!")
        return
    
    # O'yin sessiyasini yaratish
    battle_id = f"{player1_id}_{player2_id}"
    
    pvp_sessions[battle_id] = {
        'player1_id': player1_id,
        'player2_id': player2_id,
        'questions': questions,
        'player1_answers': {},
        'player2_answers': {},
        'player1_done': False,
        'player2_done': False
    }
    
    player1_username = bot.get_chat(player1_id).username or bot.get_chat(player1_id).first_name
    player2_username = bot.get_chat(player2_id).username or bot.get_chat(player2_id).first_name
    
    # Har ikkala o'yinchiga xabar
    bot.send_message(
        player1_id,
        f"⚔️ PVP BATTLE BOSHLANDI!\n\n"
        f"👤 Siz vs @{player2_username}\n\n"
        f"📝 5 ta savol\n"
        f"⚡ Tez javob bering!\n\n"
        f"Savollar boshlanmoqda..."
    )
    
    bot.send_message(
        player2_id,
        f"⚔️ PVP BATTLE BOSHLANDI!\n\n"
        f"👤 @{player1_username} vs Siz\n\n"
        f"📝 5 ta savol\n"
        f"⚡ Tez javob bering!\n\n"
        f"Savollar boshlanmoqda..."
    )
    
    # Savollarni yuborish
    import time
    time.sleep(2)
    
    send_pvp_questions(battle_id, player1_id, 0)
    send_pvp_questions(battle_id, player2_id, 0)


def send_pvp_questions(battle_id, player_id, question_index):
    """PvP savollarini yuborish"""
    if battle_id not in pvp_sessions:
        return
    
    session = pvp_sessions[battle_id]
    questions = session['questions']
    
    if question_index >= len(questions):
        # Barcha savollar tugadi
        check_player_done(battle_id, player_id)
        return
    
    question_data = questions[question_index]
    q_id, question, opt_a, opt_b, opt_c, opt_d, correct, explanation = question_data
    
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(f"A) {opt_a}", callback_data=f"pvp_{battle_id}_{question_index}_A"),
        types.InlineKeyboardButton(f"B) {opt_b}", callback_data=f"pvp_{battle_id}_{question_index}_B")
    )
    markup.row(
        types.InlineKeyboardButton(f"C) {opt_c}", callback_data=f"pvp_{battle_id}_{question_index}_C"),
        types.InlineKeyboardButton(f"D) {opt_d}", callback_data=f"pvp_{battle_id}_{question_index}_D")
    )
    
    bot.send_message(
        player_id,
        f"❓ Savol {question_index + 1}/5\n\n"
        f"{question}\n\n"
        f"A) {opt_a}\n"
        f"B) {opt_b}\n"
        f"C) {opt_c}\n"
        f"D) {opt_d}",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('pvp_') and '_' in call.data and call.data.count('_') >= 3)
def pvp_answer_handler(call):
    """PvP javoblarni qayta ishlash"""
    parts = call.data.split('_')
    
    if len(parts) < 4:
        return
    
    battle_id = f"{parts[1]}_{parts[2]}"
    question_index = int(parts[3])
    user_answer = parts[4]
    player_id = call.from_user.id
    
    if battle_id not in pvp_sessions:
        bot.answer_callback_query(call.id, "❌ O'yin tugagan!")
        return
    
    session = pvp_sessions[battle_id]
    questions = session['questions']
    question_data = questions[question_index]
    correct_answer = question_data[6]
    
    # Javobni saqlash
    player_key = 'player1_answers' if player_id == session['player1_id'] else 'player2_answers'
    session[player_key][question_index] = (user_answer == correct_answer)
    
    # Javob to'g'ri/noto'g'ri
    if user_answer == correct_answer:
        bot.answer_callback_query(call.id, "✅ To'g'ri!")
        bot.send_message(call.message.chat.id, "✅ To'g'ri javob!")
    else:
        bot.answer_callback_query(call.id, f"❌ Noto'g'ri! To'g'ri: {correct_answer}")
        bot.send_message(call.message.chat.id, f"❌ Noto'g'ri! To'g'ri javob: {correct_answer}")
    
    # Keyingi savol
    import time
    time.sleep(1)
    send_pvp_questions(battle_id, player_id, question_index + 1)


def check_player_done(battle_id, player_id):
    """O'yinchi tugatganini belgilash"""
    if battle_id not in pvp_sessions:
        return
    
    session = pvp_sessions[battle_id]
    
    if player_id == session['player1_id']:
        session['player1_done'] = True
        bot.send_message(player_id, "✅ Siz barcha savollarga javob berdingiz!\n⏳ Raqibingizni kutaylik...")
    else:
        session['player2_done'] = True
        bot.send_message(player_id, "✅ Siz barcha savollarga javob berdingiz!\n⏳ Raqibingizni kutaylik...")
    
    # Agar ikkalasi ham tugasa
    if session['player1_done'] and session['player2_done']:
        finish_pvp_battle(battle_id)


def finish_pvp_battle(battle_id):
    """PvP jangni yakunlash"""
    if battle_id not in pvp_sessions:
        return
    
    session = pvp_sessions[battle_id]
    
    player1_id = session['player1_id']
    player2_id = session['player2_id']
    
    # Natijalarni hisoblash
    player1_correct = sum(session['player1_answers'].values())
    player2_correct = sum(session['player2_answers'].values())
    
    player1_username = bot.get_chat(player1_id).username or bot.get_chat(player1_id).first_name
    player2_username = bot.get_chat(player2_id).username or bot.get_chat(player2_id).first_name
    
    # G'olibni aniqlash
    if player1_correct > player2_correct:
        winner_id = player1_id
        loser_id = player2_id
        winner_name = player1_username
        result_text = f"🏆 G'OLIB: @{winner_name}!"
        is_draw = False
    elif player2_correct > player1_correct:
        winner_id = player2_id
        loser_id = player1_id
        winner_name = player2_username
        result_text = f"🏆 G'OLIB: @{winner_name}!"
        is_draw = False
    else:
        winner_id = None
        loser_id = None
        result_text = "🤝 DURANG!"
        is_draw = True
    
    # Umumiy natija xabari
    result = (
        f"⚔️ PVP BATTLE YAKUNLANDI!\n\n"
        f"👤 @{player1_username}: {player1_correct}/5 ✅\n"
        f"👤 @{player2_username}: {player2_correct}/5 ✅\n\n"
        f"{result_text}"
    )
    
    # XP berish (faqat g'olibga)
    if not is_draw:
        xp_gained = 50  # PvP uchun 50 XP
        asyncio.run(update_user_xp(winner_id, xp_gained))
        result += f"\n\n⭐ @{winner_name} +{xp_gained} XP oldi!"
    
    bot.send_message(player1_id, result)
    bot.send_message(player2_id, result)
    
    # Statistikani yangilash
    if is_draw:
        asyncio.run(update_pvp_stats(player1_id, player2_id, is_draw=True))
    else:
        asyncio.run(update_pvp_stats(winner_id, loser_id, is_draw=False))
    
    # Tarixga saqlash
    asyncio.run(save_pvp_battle(player1_id, player2_id, player1_correct, player2_correct, winner_id))
    
    # Sessiyani o'chirish
    del pvp_sessions[battle_id]


# ==================== PVP STATISTIKA ====================

@bot.message_handler(func=lambda m: m.text == "📊 PvP Statistika")
def show_pvp_stats(message):
    """Shaxsiy PvP statistika"""
    user_id = message.from_user.id
    
    wins, losses, draws, total = asyncio.run(get_pvp_stats(user_id))
    
    if total > 0:
        win_rate = (wins / total) * 100
    else:
        win_rate = 0
    
    bot.send_message(
        message.chat.id,
        f"📊 SIZNING PVP STATISTIKANGIZ\n\n"
        f"🏆 G'alabalar: {wins}\n"
        f"❌ Mag'lubiyatlar: {losses}\n"
        f"🤝 Duranglar: {draws}\n"
        f"📊 Jami janglar: {total}\n"
        f"📈 G'alaba foizi: {win_rate:.1f}%\n\n"
        f"⚔️ Davom eting va reytingingizni oshiring!"
    )


# ==================== PVP REYTINGI ====================

@bot.message_handler(func=lambda m: m.text == "🏆 PvP Reytingi")
def show_pvp_leaderboard(message):
    """PvP reytingi"""
    leaderboard = asyncio.run(get_pvp_leaderboard(10))
    
    if not leaderboard:
        bot.send_message(message.chat.id, "❌ Hali PvP o'yinlar bo'lmagan!")
        return
    
    text = "🏆 PVP REYTINGI\n"
    text += "Top 10 o'yinchilar\n"
    text += "━━━━━━━━━━━━━━━━━━━\n\n"
    
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    
    for i, (username, wins, losses, draws, total, win_rate) in enumerate(leaderboard, 1):
        medal = medals.get(i, f"{i}.")
        user_display = f"@{username}" if username else "Anonim"
        
        text += f"{medal} {user_display}\n"
        text += f"   🏆 {wins} g'alaba | ❌ {losses} mag'lubiyat\n"
        text += f"   📊 {total} jang | 📈 {win_rate:.1f}% g'alaba\n\n"
    
    bot.send_message(message.chat.id, text)


# ==================== ORQAGA TUGMASI ====================

@bot.message_handler(func=lambda m: m.text == "🔙 Orqaga")
def back_from_pvp(message):
    """PvP dan orqaga"""
    start_command(message)

# ==================== FOYDALANUVCHI - O'RGANISH BO'LIMI ====================

@bot.message_handler(func=lambda m: m.text == "📚 O'rganish")
def learning_section(message):
    """O'rganish bo'limi - mavzular ro'yxati"""
    topics = asyncio.run(get_all_topics())
    
    if not topics:
        bot.send_message(
            message.chat.id,
            "📚 O'rganish bo'limi\n\n"
            "❌ Hozircha mavzular yo'q.\n"
            "Admin tez orada qo'shadi! 📖"
        )
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for topic_id, title, order_num in topics:
        markup.add(
            types.InlineKeyboardButton(
                f"📖 {title}",
                callback_data=f"topic_{topic_id}"
            )
        )
    
    bot.send_message(
        message.chat.id,
        "📚 O'RGANISH BO'LIMI\n\n"
        f"Jami mavzular: {len(topics)}\n\n"
        "Kerakli mavzuni tanlang:",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('topic_'))
def show_topic(call):
    """Mavzuni ko'rsatish"""
    topic_id = int(call.data.split('_')[1])
    topic = asyncio.run(get_topic_by_id(topic_id))
    
    if not topic:
        bot.answer_callback_query(call.id, "❌ Mavzu topilmadi!")
        return
    
    topic_id, title, content = topic
    
    # Orqaga qaytish tugmasi
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_topics"))
    
    bot.answer_callback_query(call.id)
    
    # Agar matn juda uzun bo'lsa, bo'laklarga ajratish
    max_length = 4000
    
    header = f"📖 {title}\n{'━' * 30}\n\n"
    
    if len(header + content) > max_length:
        bot.send_message(call.message.chat.id, header)
        
        # Matnni bo'laklarga ajratish
        parts = []
        current = ""
        for paragraph in content.split('\n\n'):
            if len(current) + len(paragraph) + 2 < max_length:
                current += paragraph + '\n\n'
            else:
                if current:
                    parts.append(current)
                current = paragraph + '\n\n'
        
        if current:
            parts.append(current)
        
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                bot.send_message(call.message.chat.id, part, reply_markup=markup)
            else:
                bot.send_message(call.message.chat.id, part)
    else:
        full_message = header + content
        bot.send_message(call.message.chat.id, full_message, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_topics")
def back_to_topics(call):
    """Mavzular ro'yxatiga qaytish"""
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    # Mavzular ro'yxatini qayta ko'rsatish
    topics = asyncio.run(get_all_topics())
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for topic_id, title, order_num in topics:
        markup.add(
            types.InlineKeyboardButton(
                f"📖 {title}",
                callback_data=f"topic_{topic_id}"
            )
        )
    
    bot.send_message(
        call.message.chat.id,
        "📚 O'RGANISH BO'LIMI\n\n"
        f"Jami mavzular: {len(topics)}\n\n"
        "Kerakli mavzuni tanlang:",
        reply_markup=markup
    )


# ==================== ADMIN PANEL ====================


# ==================== ADMIN PANEL YANGILASH ====================

@bot.message_handler(func=lambda m: m.text == "⚙️ Admin Panel" and m.from_user.id == ADMIN_ID)
def admin_panel(message):
    """Admin panel - PvP statistika bilan"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("➕ Savol qo'shish", "📊 Savollar soni")
    markup.row("📈 Umumiy Statistika")
    markup.row("🏆 Mavsum Statistikasi")
    markup.row("📚 O'rganish Boshqaruvi")
    markup.row("📢 Xabar Yuborish")
    markup.row("📤 Kanalga Post", "🎖 Top Darajalar")
    markup.row("⚔️ PvP Statistika")
    markup.row("🏆 Turnir Boshqaruvi")
    markup.row("💎 Premium Boshqaruvi")
    markup.row("🔙 Orqaga")
    
    bot.send_message(
        message.chat.id,
        "⚙️ Admin panel\n\nKerakli bo'limni tanlang:",
        reply_markup=markup
    )



@bot.message_handler(func=lambda m: m.text == "📤 Kanalga Post" and m.from_user.id == ADMIN_ID)
def channel_post_menu(message):
    """Kanalga post yuborish menyusi"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📊 Kunlik Top", "👑 Haftalik Top")
    markup.row("🔙 Admin Panelga")
    
    bot.send_message(
        message.chat.id,
        "📤 Kanalga Post\n\n"
        "Qaysi postni yubormoqchisiz?",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text == "📊 Kunlik Top" and m.from_user.id == ADMIN_ID)
def manual_daily_post(message):
    """Qo'lda kunlik top yuborish"""
    bot.send_message(message.chat.id, "⏳ Post tayyorlanmoqda...")
    send_daily_leaderboard()
    bot.send_message(message.chat.id, "✅ Kunlik top kanalga yuborildi!")


@bot.message_handler(func=lambda m: m.text == "👑 Haftalik Top" and m.from_user.id == ADMIN_ID)
def manual_weekly_post(message):
    """Qo'lda haftalik top yuborish"""
    bot.send_message(message.chat.id, "⏳ Post tayyorlanmoqda...")
    send_weekly_season_top()
    bot.send_message(message.chat.id, "✅ Haftalik top kanalga yuborildi!")


@bot.message_handler(func=lambda m: m.text == "🎖 Top Darajalar" and m.from_user.id == ADMIN_ID)
def show_top_levels(message):
    """Top darajadagilar (admin uchun)"""
    top_users = asyncio.run(get_top_users_by_level(20))
    
    if not top_users:
        bot.send_message(message.chat.id, "❌ Hali foydalanuvchilar yo'q!")
        return
    
    text = "🎖 TOP 20 DARAJA BO'YICHA\n\n"
    
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    
    for i, (username, level, xp) in enumerate(top_users, 1):
        medal = medals.get(i, f"{i}.")
        user_display = f"@{username}" if username else "Anonim"
        level_name = get_level_name(level)
        
        text += f"{medal} {user_display}\n"
        text += f"   {level_name}\n"
        text += f"   ⭐ {xp} XP\n\n"
    
    if len(text) > 4000:
        parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for part in parts:
            bot.send_message(message.chat.id, part)
    else:
        bot.send_message(message.chat.id, text)

# ==================== UMUMIY STATISTIKA HANDLER ====================
# Admin handlerlar bo'limiga qo'shing

@bot.message_handler(func=lambda m: m.text == "📈 Umumiy Statistika" and m.from_user.id == ADMIN_ID)
def show_overall_statistics(message):
    """Umumiy statistikani ko'rsatish"""
    bot.send_message(message.chat.id, "⏳ Statistika tayyorlanmoqda...")
    
    stats = asyncio.run(get_overall_statistics())
    
    # Asosiy statistika
    text = "📊 UMUMIY STATISTIKA\n"
    text += "━━━━━━━━━━━━━━━━━━━\n\n"
    text += f"👥 Jami foydalanuvchilar: {stats['total_users']}\n"
    text += f"📝 Jami quizlar: {stats['total_quizzes']}\n"
    text += f"❓ Bazadagi savollar: {stats['total_questions']}\n\n"
    
    # Top 20 foydalanuvchilar
    text += "🏆 TOP 20 FOYDALANUVCHILAR\n"
    text += "(To'g'ri javoblar bo'yicha)\n"
    text += "━━━━━━━━━━━━━━━━━━━\n\n"
    
    if not stats['top_users']:
        text += "❌ Hali statistika yo'q\n"
    else:
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        
        for i, (username, correct, wrong, quizzes, accuracy) in enumerate(stats['top_users'], 1):
            medal = medals.get(i, f"{i}.")
            user_display = f"@{username}" if username else "Anonim"
            
            text += f"{medal} {user_display}\n"
            text += f"   ✅ To'g'ri: {correct}\n"
            text += f"   🎯 Quizlar: {quizzes}\n"
            text += f"   📊 Aniqlik: {accuracy:.1f}%\n\n"
    
    # Xabarni bo'laklarga ajratish (Telegram 4096 belgi limiti)
    if len(text) > 4000:
        # Birinchi qism - asosiy ma'lumotlar
        part1 = text[:text.find("🏆 TOP 20")]
        bot.send_message(message.chat.id, part1)
        
        # Ikkinchi qism - top foydalanuvchilar
        part2 = text[text.find("🏆 TOP 20"):]
        
        # Agar ikkinchi qism ham katta bo'lsa
        while len(part2) > 4000:
            split_point = part2.rfind('\n\n', 0, 4000)
            bot.send_message(message.chat.id, part2[:split_point])
            part2 = part2[split_point:]
        
        bot.send_message(message.chat.id, part2)
    else:
        bot.send_message(message.chat.id, text)
    
    bot.send_message(message.chat.id, "✅ Statistika tayyor!")
    
 
# ==================== MAVSUM STATISTIKASI MENU ====================

@bot.message_handler(func=lambda m: m.text == "🏆 Mavsum Statistikasi" and m.from_user.id == ADMIN_ID)
def season_stats_menu(message):
    """Mavsum statistikasi menyusi"""
    season_info = asyncio.run(get_season_info())
    season_num, season_name, start_date, is_active = season_info
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📊 Hozirgi Mavsum", "🗂 Mavsum Tarixi")
    markup.row("🔄 Yangi Mavsum Boshlash")
    markup.row("🔙 Admin Panelga")
    
    bot.send_message(
        message.chat.id,
        f"🏆 Mavsum Statistikasi\n\n"
        f"📅 Hozirgi: {season_name} (#{season_num})\n"
        f"📆 Boshlangan: {start_date[:10]}\n"
        f"🔥 Status: {'Faol' if is_active else 'Tugagan'}\n\n"
        f"Kerakli bo'limni tanlang:",
        reply_markup=markup
    )


# ==================== HOZIRGI MAVSUM ====================

@bot.message_handler(func=lambda m: m.text == "📊 Hozirgi Mavsum" and m.from_user.id == ADMIN_ID)
def show_current_season(message):
    """Hozirgi mavsum statistikasi"""
    bot.send_message(message.chat.id, "⏳ Statistika tayyorlanmoqda...")
    
    season_info = asyncio.run(get_season_info())
    season_num, season_name, start_date, is_active = season_info
    
    top_users = asyncio.run(get_season_top_users(20))
    
    text = f"🏆 {season_name.upper()}\n"
    text += f"📅 Mavsum #{season_num}\n"
    text += f"📆 Boshlangan: {start_date[:10]}\n"
    text += "━━━━━━━━━━━━━━━━━━━\n\n"
    text += "👑 TOP 20 FOYDALANUVCHILAR\n"
    text += "(To'g'ri javoblar bo'yicha)\n"
    text += "━━━━━━━━━━━━━━━━━━━\n\n"
    
    if not top_users:
        text += "❌ Hali statistika yo'q\n"
    else:
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        
        for i, (username, correct, wrong, quizzes, accuracy) in enumerate(top_users, 1):
            medal = medals.get(i, f"{i}.")
            user_display = f"@{username}" if username else "Anonim"
            
            text += f"{medal} {user_display}\n"
            text += f"   ✅ To'g'ri: {correct}\n"
            text += f"   ❌ Noto'g'ri: {wrong}\n"
            text += f"   🎯 Quizlar: {quizzes}\n"
            text += f"   📊 Aniqlik: {accuracy:.1f}%\n\n"
    
    # Xabarni bo'laklarga ajratish
    if len(text) > 4000:
        parts = []
        current = ""
        for line in text.split('\n'):
            if len(current) + len(line) < 4000:
                current += line + '\n'
            else:
                parts.append(current)
                current = line + '\n'
        parts.append(current)
        
        for part in parts:
            bot.send_message(message.chat.id, part)
    else:
        bot.send_message(message.chat.id, text)


# ==================== MAVSUM TARIXI ====================

@bot.message_handler(func=lambda m: m.text == "🗂 Mavsum Tarixi" and m.from_user.id == ADMIN_ID)
def show_season_history(message):
    """Mavsum tarixi"""
    history = asyncio.run(get_season_history(10))
    
    if not history:
        bot.send_message(message.chat.id, "❌ Hali tugagan mavsum yo'q!")
        return
    
    text = "🗂 MAVSUM TARIXI\n"
    text += "━━━━━━━━━━━━━━━━━━━\n\n"
    
    for season_num, season_name, start, end, winner, score in history:
        text += f"🏆 {season_name}\n"
        text += f"📅 {start[:10]} - {end[:10]}\n"
        text += f"👑 G'olib: @{winner if winner else 'Anonim'}\n"
        text += f"⭐ Ball: {score}\n\n"
    
    bot.send_message(message.chat.id, text)


# ==================== YANGI MAVSUM BOSHLASH ====================

@bot.message_handler(func=lambda m: m.text == "🔄 Yangi Mavsum Boshlash" and m.from_user.id == ADMIN_ID)
def new_season_confirm(message):
    """Yangi mavsum boshlash tasdiqlash"""
    season_info = asyncio.run(get_season_info())
    season_num, season_name, start_date, is_active = season_info
    
    top_users = asyncio.run(get_season_top_users(1))
    
    if top_users:
        winner_name = top_users[0][0]
        winner_score = top_users[0][1]
        winner_text = f"👑 Hozirgi lider: @{winner_name if winner_name else 'Anonim'} ({winner_score} ball)"
    else:
        winner_text = "❌ Hali ishtirokchilar yo'q"
    
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Ha, boshlash", callback_data="new_season_yes"),
        types.InlineKeyboardButton("❌ Yo'q, bekor", callback_data="new_season_no")
    )
    
    bot.send_message(
        message.chat.id,
        f"⚠️ DIQQAT!\n\n"
        f"Yangi mavsum boshlash:\n"
        f"• Hozirgi mavsum ({season_name}) tugaydi\n"
        f"• G'olib tarixga saqlanadi\n"
        f"• Barcha statistika 0 ga tushadi\n"
        f"• Yangi {season_num + 1}-mavsum boshlanadi\n\n"
        f"{winner_text}\n\n"
        f"Davom etishni xohlaysizmi?",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == "new_season_yes")
def new_season_start(call):
    """Yangi mavsumni boshlash"""
    bot.answer_callback_query(call.id, "⏳ Mavsum boshlanmoqda...")
    
    # G'olibni saqlash
    winner_name, winner_score = asyncio.run(save_season_winner())
    
    # Statistikani tozalash
    asyncio.run(reset_season_stats())
    
    # Yangi mavsumni boshlash
    season_info = asyncio.run(get_season_info())
    new_season_num = season_info[0] + 1
    new_season_name = f"Mavsum {new_season_num}"
    
    asyncio.run(start_new_season(new_season_name))
    
    # Natija
    result_text = f"✅ Yangi mavsum boshlandi!\n\n"
    result_text += f"🏆 {new_season_name}\n\n"
    
    if winner_name:
        result_text += f"🎉 O'tgan mavsum g'olibi:\n"
        result_text += f"👑 @{winner_name}\n"
        result_text += f"⭐ {winner_score} ball\n\n"
    
    result_text += f"📊 Barcha statistika 0 ga tushirildi.\n"
    result_text += f"🚀 Musobaqa boshlandi!"
    
    bot.send_message(call.message.chat.id, result_text)


@bot.callback_query_handler(func=lambda call: call.data == "new_season_no")
def new_season_cancel(call):
    """Yangi mavsumni bekor qilish"""
    bot.answer_callback_query(call.id, "❌ Bekor qilindi")
    bot.send_message(call.message.chat.id, "❌ Yangi mavsum boshlash bekor qilindi.")


# ==================== ORQAGA TUGMASI ====================

@bot.message_handler(func=lambda m: m.text == "🔙 Admin Panelga" and m.from_user.id == ADMIN_ID)
def back_to_admin_panel_from_season(message):
    """Admin panelga qaytish"""
    admin_panel(message)



# ==================== AVTOMATIK KEYINGI SAVOL (30 SONIYA) ====================
# Joylashtirish: send_group_question funksiyasidan oldin

def auto_next_question(group_id, question_index):
    """30 soniyadan keyin avtomatik keyingi savol"""
    import time
    time.sleep(30)  # 30 soniya kutish
    
    if group_id not in group_quiz_sessions:
        return
    
    session = group_quiz_sessions[group_id]
    
    # Hali shu savolda ekanini tekshirish
    if session['current'] != question_index:
        return  # Allaqachon keyingi savolga o'tilgan
    
    # Hozirgi savol natijasini ko'rsatish
    question_data = session['questions'][question_index]
    correct_answer = question_data[6]
    explanation = question_data[7]
    
    # Shu savolda necha kishi javob berganini hisoblash
    answered_count = len([
        uid for uid, data in session['participants'].items()
        if 'answered_questions' in data and question_index in data['answered_questions']
    ])
    
    result_text = f"⏰ Vaqt tugadi!\n\n✅ To'g'ri javob: {correct_answer}"
    
    if explanation:
        result_text += f"\n\n💡 Izoh: {explanation}"
    
    result_text += f"\n\n👥 Javob berganlar: {answered_count}"
    
    bot.send_message(group_id, result_text)
    
    # Keyingi savolga o'tish
    session['current'] += 1
    
    if session['current'] >= len(session['questions']):
        # Quiz tugadi
        import time
        time.sleep(2)
        finish_group_quiz(group_id)
    else:
        # Keyingi savol
        import time
        time.sleep(2)
        send_group_question(group_id)


# ==================== YANGILANGAN send_group_question ====================
# Eski send_group_question funksiyasini bu versiya bilan ALMASHTIRING

def send_group_question(group_id):
    """Guruh quiziga savol yuborish (timer bilan)"""
    if group_id not in group_quiz_sessions:
        return
    
    session = group_quiz_sessions[group_id]
    
    # Barcha savollar tugadimi?
    if session['current'] >= len(session['questions']):
        finish_group_quiz(group_id)
        return
    
    question_data = session['questions'][session['current']]
    q_id, question, opt_a, opt_b, opt_c, opt_d, correct, explanation = question_data
    
    # Inline tugmalar
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("A", callback_data=f"gq_{group_id}_{session['current']}_A"),
        types.InlineKeyboardButton("B", callback_data=f"gq_{group_id}_{session['current']}_B"),
        types.InlineKeyboardButton("C", callback_data=f"gq_{group_id}_{session['current']}_C"),
        types.InlineKeyboardButton("D", callback_data=f"gq_{group_id}_{session['current']}_D")
    )
    
    current_num = session['current'] + 1
    
    question_text = (
        f"❓ Savol {current_num}/10\n"
        f"⏰ 30 soniya\n\n"
        f"{question}\n\n"
        f"🅰️ {opt_a}\n"
        f"🅱️ {opt_b}\n"
        f"🅲️ {opt_c}\n"
        f"🅳️ {opt_d}"
    )
    
    msg = bot.send_message(group_id, question_text, reply_markup=markup)
    session['message_ids'].append(msg.message_id)
    
    # AVTOMATIK TIMER BOSHLASH
    import threading
    timer = threading.Thread(
        target=auto_next_question,
        args=(group_id, session['current'])
    )
    timer.daemon = True
    timer.start()


# ==================== YANGILANGAN group_quiz_answer ====================
# Eski group_quiz_answer funksiyasini bu versiya bilan ALMASHTIRING

@bot.callback_query_handler(func=lambda call: call.data.startswith('gq_'))
def group_quiz_answer(call):
    """Guruh quiz javobini qayta ishlash"""
    parts = call.data.split('_')
    group_id = int(parts[1])
    question_index = int(parts[2])
    user_answer = parts[3]
    
    user_id = call.from_user.id
    user_name = call.from_user.first_name
    
    # Sessiya mavjudmi?
    if group_id not in group_quiz_sessions:
        bot.answer_callback_query(call.id, "❌ Quiz tugagan!")
        return
    
    session = group_quiz_sessions[group_id]
    
    # Noto'g'ri savol indexi
    if session['current'] != question_index:
        bot.answer_callback_query(call.id, "❌ Bu savol allaqachon o'tgan!")
        return
    
    # Foydalanuvchini qo'shish (agar yo'q bo'lsa)
    if user_id not in session['participants']:
        session['participants'][user_id] = {
            'name': user_name,
            'score': 0,
            'answered_questions': []
        }
    
    # Foydalanuvchi bu savolga allaqachon javob berganmi?
    if question_index in session['participants'][user_id]['answered_questions']:
        bot.answer_callback_query(call.id, "✅ Siz allaqachon javob berdingiz!")
        return
    
    # Javobni tekshirish
    question_data = session['questions'][question_index]
    correct_answer = question_data[6]
    
    is_correct = (user_answer == correct_answer)
    
    # Javob berganini belgilash
    session['participants'][user_id]['answered_questions'].append(question_index)
    
    if is_correct:
        session['participants'][user_id]['score'] += 1
        bot.answer_callback_query(call.id, "✅ To'g'ri!")
    else:
        bot.answer_callback_query(call.id, f"❌ Noto'g'ri! To'g'ri: {correct_answer}")


# ==================== YANGILANGAN next_group_question ====================
# /next buyrug'i endi timerni to'xtatadi va darhol keyingi savolga o'tadi

@bot.message_handler(commands=['next', 'keyingi'])
def next_group_question(message):
    """Keyingi savolga o'tish (timer to'xtatiladi)"""
    if message.chat.type not in ['group', 'supergroup']:
        return
    
    group_id = message.chat.id
    
    if group_id not in group_quiz_sessions:
        bot.reply_to(message, "❌ Hozir faol quiz yo'q!")
        return
    
    session = group_quiz_sessions[group_id]
    
    # Faqat admin yoki quiz boshlagan odam
    user_id = message.from_user.id
    
    try:
        chat_member = bot.get_chat_member(group_id, user_id)
        is_admin = chat_member.status in ['creator', 'administrator']
    except:
        is_admin = False
    
    if not is_admin and user_id != session['admin_id']:
        bot.reply_to(message, "❌ Faqat admin yoki quiz boshlagan odam o'tkazishi mumkin!")
        return
    
    # Hozirgi savol natijasini ko'rsatish
    question_data = session['questions'][session['current']]
    correct_answer = question_data[6]
    explanation = question_data[7]
    
    result_text = f"✅ To'g'ri javob: {correct_answer}"
    if explanation:
        result_text += f"\n\n💡 Izoh: {explanation}"
    
    # Shu savolda ishtirok etganlar soni
    answered_count = len([
        uid for uid, data in session['participants'].items()
        if 'answered_questions' in data and session['current'] in data['answered_questions']
    ])
    result_text += f"\n\n👥 Javob berganlar: {answered_count}"
    
    bot.send_message(group_id, result_text)
    
    # Keyingi savolga o'tish
    session['current'] += 1
    
    if session['current'] >= len(session['questions']):
        import time
        time.sleep(2)
        finish_group_quiz(group_id)
    else:
        # Keyingi savol
        import time
        time.sleep(2)
        send_group_question(group_id)


# ==================== ADMIN - O'RGANISH BOSHQARUVI ====================

@bot.message_handler(func=lambda m: m.text == "📚 O'rganish Boshqaruvi" and m.from_user.id == ADMIN_ID)
def learning_admin_menu(message):
    """O'rganish boshqaruvi menyusi"""
    topics_count = asyncio.run(get_topics_count())
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("➕ Mavzu Qo'shish", "📋 Mavzular Ro'yxati")
    markup.row("✏️ Mavzu Tahrirlash", "🗑 Mavzu O'chirish")
    markup.row("🔙 Admin Panelga")
    
    bot.send_message(
        message.chat.id,
        f"📚 O'rganish Boshqaruvi\n\n"
        f"📊 Jami mavzular: {topics_count}\n\n"
        f"Kerakli bo'limni tanlang:",
        reply_markup=markup
    )


# ==================== MAVZU QO'SHISH ====================

@bot.message_handler(func=lambda m: m.text == "➕ Mavzu Qo'shish" and m.from_user.id == ADMIN_ID)
def add_topic_start(message):
    """Mavzu qo'shish boshlash"""
    admin_sessions[message.from_user.id] = {'type': 'add_topic', 'step': 1}
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("❌ Bekor qilish")
    
    bot.send_message(
        message.chat.id,
        "📚 Yangi mavzu qo'shish\n\n"
        "1️⃣ Mavzu nomini kiriting:\n"
        "(Masalan: Kvadrat tenglama, Tub sonlar va h.k.)",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and 
                     m.from_user.id in admin_sessions and 
                     admin_sessions[m.from_user.id].get('type') == 'add_topic')
def add_topic_process(message):
    """Mavzu qo'shish jarayoni"""
    admin_id = message.from_user.id
    session = admin_sessions[admin_id]
    
    if message.text == "❌ Bekor qilish":
        del admin_sessions[admin_id]
        learning_admin_menu(message)
        return
    
    if session['step'] == 1:
        session['title'] = message.text
        session['step'] = 2
        
        bot.send_message(
            message.chat.id,
            "2️⃣ Mavzu mazmunini kiriting:\n\n"
            "💡 Maslahatlar:\n"
            "• Matn, rasm, video yuborishingiz mumkin\n"
            "• Matnni bo'laklarga ajrating\n"
            "• Emoji ishlatishingiz mumkin\n"
            "• Uzun matnlar uchun bir necha xabar yuboring\n\n"
            "Mazmunni yozing:"
        )
    
    elif session['step'] == 2:
        # Mazmunni saqlash
        if message.text:
            content = message.text
        elif message.caption:
            content = message.caption + "\n\n[Rasm yuborilgan]"
        else:
            content = "[Media fayl]"
        
        session['content'] = content
        
        # Tasdiqlash
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("✅ Saqlash", callback_data="save_topic"),
            types.InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_topic")
        )
        
        preview = content[:200] + "..." if len(content) > 200 else content
        
        bot.send_message(
            message.chat.id,
            f"📚 Mavzu ko'rinishi:\n\n"
            f"📖 {session['title']}\n"
            f"{'━' * 30}\n\n"
            f"{preview}\n\n"
            f"Saqlashni xohlaysizmi?",
            reply_markup=markup
        )


@bot.callback_query_handler(func=lambda call: call.data == "save_topic")
def save_topic(call):
    """Mavzuni saqlash"""
    admin_id = call.from_user.id
    
    if admin_id not in admin_sessions:
        bot.answer_callback_query(call.id, "❌ Sessiya tugagan!")
        return
    
    session = admin_sessions[admin_id]
    
    asyncio.run(add_topic(session['title'], session['content']))
    
    bot.answer_callback_query(call.id, "✅ Saqlandi!")
    bot.send_message(
        call.message.chat.id,
        f"✅ Mavzu muvaffaqiyatli qo'shildi!\n\n"
        f"📖 {session['title']}"
    )
    
    del admin_sessions[admin_id]
    learning_admin_menu(call.message)


@bot.callback_query_handler(func=lambda call: call.data == "cancel_topic")
def cancel_topic(call):
    """Mavzu qo'shishni bekor qilish"""
    admin_id = call.from_user.id
    
    if admin_id in admin_sessions:
        del admin_sessions[admin_id]
    
    bot.answer_callback_query(call.id, "❌ Bekor qilindi")
    bot.send_message(call.message.chat.id, "❌ Mavzu qo'shish bekor qilindi.")
    learning_admin_menu(call.message)


# ==================== MAVZULAR RO'YXATI ====================

@bot.message_handler(func=lambda m: m.text == "📋 Mavzular Ro'yxati" and m.from_user.id == ADMIN_ID)
def list_topics_admin(message):
    """Mavzular ro'yxati (admin uchun)"""
    topics = asyncio.run(get_all_topics())
    
    if not topics:
        bot.send_message(message.chat.id, "❌ Hali mavzular yo'q!")
        return
    
    text = "📋 MAVZULAR RO'YXATI\n\n"
    
    for i, (topic_id, title, order_num) in enumerate(topics, 1):
        text += f"{i}. {title} (ID: {topic_id})\n"
    
    text += f"\n📊 Jami: {len(topics)} ta mavzu"
    
    bot.send_message(message.chat.id, text)


# ==================== MAVZU O'CHIRISH ====================

@bot.message_handler(func=lambda m: m.text == "🗑 Mavzu O'chirish" and m.from_user.id == ADMIN_ID)
def delete_topic_start(message):
    """Mavzu o'chirish boshlash"""
    topics = asyncio.run(get_all_topics())
    
    if not topics:
        bot.send_message(message.chat.id, "❌ O'chiriladigan mavzu yo'q!")
        return
    
    admin_sessions[message.from_user.id] = {'type': 'delete_topic', 'step': 1}
    
    text = "🗑 Mavzu o'chirish\n\n"
    text += "Mavzular ro'yxati:\n\n"
    
    for i, (topic_id, title, order_num) in enumerate(topics, 1):
        text += f"{i}. {title} (ID: {topic_id})\n"
    
    text += "\nO'chirmoqchi bo'lgan mavzu ID sini kiriting:"
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("❌ Bekor qilish")
    
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and 
                     m.from_user.id in admin_sessions and 
                     admin_sessions[m.from_user.id].get('type') == 'delete_topic')
def delete_topic_process(message):
    """Mavzu o'chirish jarayoni"""
    admin_id = message.from_user.id
    
    if message.text == "❌ Bekor qilish":
        del admin_sessions[admin_id]
        learning_admin_menu(message)
        return
    
    try:
        topic_id = int(message.text)
        topic = asyncio.run(get_topic_by_id(topic_id))
        
        if not topic:
            bot.send_message(message.chat.id, "❌ Bu ID da mavzu topilmadi!")
            return
        
        # Tasdiqlash
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("✅ Ha, o'chirish", callback_data=f"delete_confirm_{topic_id}"),
            types.InlineKeyboardButton("❌ Yo'q", callback_data="delete_cancel")
        )
        
        bot.send_message(
            message.chat.id,
            f"⚠️ Tasdiqlash\n\n"
            f"Ushbu mavzu o'chiriladi:\n"
            f"📖 {topic[1]}\n\n"
            f"Davom etishni xohlaysizmi?",
            reply_markup=markup
        )
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ Faqat raqam kiriting!")


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_confirm_'))
def delete_topic_confirm(call):
    """Mavzuni o'chirishni tasdiqlash"""
    topic_id = int(call.data.split('_')[2])
    
    asyncio.run(delete_topic(topic_id))
    
    bot.answer_callback_query(call.id, "✅ O'chirildi!")
    bot.send_message(call.message.chat.id, "✅ Mavzu muvaffaqiyatli o'chirildi!")
    
    admin_id = call.from_user.id
    if admin_id in admin_sessions:
        del admin_sessions[admin_id]
    
    learning_admin_menu(call.message)


@bot.callback_query_handler(func=lambda call: call.data == "delete_cancel")
def delete_topic_cancel(call):
    """O'chirishni bekor qilish"""
    bot.answer_callback_query(call.id, "❌ Bekor qilindi")
    bot.send_message(call.message.chat.id, "❌ O'chirish bekor qilindi.")
    
    admin_id = call.from_user.id
    if admin_id in admin_sessions:
        del admin_sessions[admin_id]
    
    learning_admin_menu(call.message)


# ==================== ORQAGA TUGMASI ====================

@bot.message_handler(func=lambda m: m.text == "🔙 Admin Panelga" and m.from_user.id == ADMIN_ID)
def back_to_admin_from_learning(message):
    """Admin panelga qaytish"""
    if message.from_user.id in admin_sessions:
        del admin_sessions[message.from_user.id]
    admin_panel(message)


    
   
# ==================== QOSHIMCHA: EKSPORT FUNKSIYASI ====================
# Agar admin statistikani fayl sifatida yuklab olishni xohlasa

@bot.message_handler(func=lambda m: m.text == "📥 Statistikani Yuklash" and m.from_user.id == ADMIN_ID)
def export_statistics(message):
    """Statistikani txt fayl sifatida yuklash"""
    bot.send_message(message.chat.id, "⏳ Fayl tayyorlanmoqda...")
    
    stats = asyncio.run(get_overall_statistics())
    
    # Fayl yaratish
    filename = "statistika.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("📊 UMUMIY STATISTIKA\n")
        f.write("━━━━━━━━━━━━━━━━━━━\n\n")
        f.write(f"👥 Jami foydalanuvchilar: {stats['total_users']}\n")
        f.write(f"📝 Jami quizlar: {stats['total_quizzes']}\n")
        f.write(f"❓ Bazadagi savollar: {stats['total_questions']}\n\n")
        f.write("🏆 TOP 20 FOYDALANUVCHILAR\n")
        f.write("(To'g'ri javoblar bo'yicha)\n")
        f.write("━━━━━━━━━━━━━━━━━━━\n\n")
        
        for i, (username, correct, wrong, quizzes, accuracy) in enumerate(stats['top_users'], 1):
            user_display = f"@{username}" if username else "Anonim"
            f.write(f"{i}. {user_display}\n")
            f.write(f"   ✅ To'g'ri: {correct}\n")
            f.write(f"   ❌ Noto'g'ri: {wrong}\n")
            f.write(f"   🎯 Quizlar: {quizzes}\n")
            f.write(f"   📊 Aniqlik: {accuracy:.1f}%\n\n")
    
    # Faylni yuborish
    with open(filename, 'rb') as f:
        bot.send_document(message.chat.id, f, caption="📊 Umumiy statistika fayli")
    
    # Faylni o'chirish
    os.remove(filename)
    bot.send_message(message.chat.id, "✅ Fayl yuborildi!")


# ==================== YANGILANGAN ADMIN PANEL (IXTIYORIY) ====================
# Agar yuklab olish funksiyasini ham qo'shmoqchi bo'lsangiz:

@bot.message_handler(func=lambda m: m.text == "⚙️ Admin Panel" and m.from_user.id == ADMIN_ID)
def admin_panel_full(message):
    """Admin panel - to'liq versiya"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("➕ Savol qo'shish", "📊 Savollar soni")
    markup.row("📈 Umumiy Statistika", "📥 Statistikani Yuklash")
    markup.row("🔙 Orqaga")
    
    bot.send_message(
        message.chat.id,
        "⚙️ Admin panel\n\n"
        "📈 Umumiy Statistika - ekranda ko'rish\n"
        "📥 Statistikani Yuklash - fayl sifatida olish\n\n"
        "Kerakli bo'limni tanlang:",
        reply_markup=markup
    )
@bot.message_handler(func=lambda m: m.text == "➕ Savol qo'shish" and m.from_user.id == ADMIN_ID)
def add_question_start(message):
    """Savol qo'shish jarayonini boshlash"""
    admin_sessions[message.from_user.id] = {'step': 1}
    bot.send_message(message.chat.id, "1️⃣ Savolni kiriting:")


@bot.message_handler(func=lambda m: m.text == "📊 Savollar soni" and m.from_user.id == ADMIN_ID)
def show_questions_count(message):
    """Savollar sonini ko'rsatish"""
    count = asyncio.run(get_questions_count())
    bot.send_message(
        message.chat.id,
        f"📊 Bazada {count} ta savol mavjud."
    )


@bot.message_handler(func=lambda m: m.text == "🔙 Orqaga" and m.from_user.id == ADMIN_ID)
def back_to_main(message):
    """Asosiy menyuga qaytish"""
    if message.from_user.id in admin_sessions:
        del admin_sessions[message.from_user.id]
    start_command(message)

  # ==================== BROADCAST MENU ====================

@bot.message_handler(func=lambda m: m.text == "📢 Xabar Yuborish" and m.from_user.id == ADMIN_ID)
def broadcast_menu(message):
    """Broadcast menyusi"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("👤 Bitta foydalanuvchiga", "👥 Barchaga")
    markup.row("🔙 Admin Panelga")
    
    bot.send_message(
        message.chat.id,
        "📢 Xabar yuborish\n\n"
        "👤 Bitta foydalanuvchiga - ID orqali\n"
        "👥 Barchaga - barcha foydalanuvchilarga\n\n"
        "Kerakli variantni tanlang:",
        reply_markup=markup
    )


# ==================== BITTA FOYDALANUVCHIGA ====================

@bot.message_handler(func=lambda m: m.text == "👤 Bitta foydalanuvchiga" and m.from_user.id == ADMIN_ID)
def broadcast_single_start(message):
    """Bitta foydalanuvchiga xabar yuborish boshlash"""
    broadcast_sessions[message.from_user.id] = {'type': 'single', 'step': 1}
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("❌ Bekor qilish")
    
    bot.send_message(
        message.chat.id,
        "👤 Bitta foydalanuvchiga xabar\n\n"
        "Foydalanuvchi ID sini kiriting:\n"
        "(Masalan: 123456789)\n\n"
        "💡 Foydalanuvchi botga /start bosgan bo'lishi kerak!",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and 
                     m.from_user.id in broadcast_sessions and 
                     broadcast_sessions[m.from_user.id]['type'] == 'single')
def broadcast_single_process(message):
    """Bitta foydalanuvchiga xabar yuborish jarayoni"""
    admin_id = message.from_user.id
    session = broadcast_sessions[admin_id]
    
    if message.text == "❌ Bekor qilish":
        del broadcast_sessions[admin_id]
        broadcast_menu(message)
        return
    
    if session['step'] == 1:
        # ID ni tekshirish
        try:
            user_id = int(message.text)
            
            # Foydalanuvchi mavjudligini tekshirish
            exists = asyncio.run(check_user_exists(user_id))
            
            if not exists:
                bot.send_message(
                    message.chat.id,
                    "❌ Bu foydalanuvchi botda ro'yxatdan o'tmagan!\n\n"
                    "Iltimos, boshqa ID kiriting yoki bekor qiling."
                )
                return
            
            session['user_id'] = user_id
            session['step'] = 2
            
            bot.send_message(
                message.chat.id,
                f"✅ Foydalanuvchi topildi: {user_id}\n\n"
                "Endi yubormoqchi bo'lgan xabaringizni yozing:\n"
                "(Matn, rasm, video yoki sticker yuborishingiz mumkin)"
            )
            
        except ValueError:
            bot.send_message(
                message.chat.id,
                "❌ Noto'g'ri format!\n\n"
                "Iltimos, faqat raqam kiriting (masalan: 123456789)"
            )
    
    elif session['step'] == 2:
        # Xabarni yuborish
        user_id = session['user_id']
        
        try:
            # Xabar turini aniqlash va yuborish
            if message.text:
                bot.send_message(user_id, message.text)
            elif message.photo:
                bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption)
            elif message.video:
                bot.send_video(user_id, message.video.file_id, caption=message.caption)
            elif message.document:
                bot.send_document(user_id, message.document.file_id, caption=message.caption)
            elif message.sticker:
                bot.send_sticker(user_id, message.sticker.file_id)
            else:
                bot.send_message(message.chat.id, "❌ Bu turdagi xabar yuborib bo'lmaydi!")
                return
            
            bot.send_message(
                message.chat.id,
                f"✅ Xabar muvaffaqiyatli yuborildi!\n"
                f"📤 Qabul qiluvchi: {user_id}"
            )
            
        except Exception as e:
            bot.send_message(
                message.chat.id,
                f"❌ Xabar yuborishda xatolik:\n{str(e)}\n\n"
                f"Foydalanuvchi botni bloklagan bo'lishi mumkin."
            )
        
        del broadcast_sessions[admin_id]
        broadcast_menu(message)


# ==================== BARCHAGA ====================

@bot.message_handler(func=lambda m: m.text == "👥 Barchaga" and m.from_user.id == ADMIN_ID)
def broadcast_all_start(message):
    """Barchaga xabar yuborish boshlash"""
    total_users = len(asyncio.run(get_all_user_ids()))
    
    broadcast_sessions[message.from_user.id] = {'type': 'all', 'step': 1}
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("❌ Bekor qilish")
    
    bot.send_message(
        message.chat.id,
        f"👥 Barchaga xabar yuborish\n\n"
        f"📊 Jami foydalanuvchilar: {total_users}\n\n"
        f"Yubormoqchi bo'lgan xabaringizni yozing:\n"
        f"(Matn, rasm, video yoki sticker yuborishingiz mumkin)\n\n"
        f"⚠️ Bu xabar barcha foydalanuvchilarga yuboriladi!",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and 
                     m.from_user.id in broadcast_sessions and 
                     broadcast_sessions[m.from_user.id]['type'] == 'all')
def broadcast_all_process(message):
    """Barchaga xabar yuborish jarayoni"""
    admin_id = message.from_user.id
    
    if message.text == "❌ Bekor qilish":
        del broadcast_sessions[admin_id]
        broadcast_menu(message)
        return
    
    # Tasdiqlash
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Ha, yuborish", callback_data="broadcast_confirm"),
        types.InlineKeyboardButton("❌ Yo'q, bekor qilish", callback_data="broadcast_cancel")
    )
    
    # Xabarni sessiyaga saqlash
    broadcast_sessions[admin_id]['message'] = message
    
    bot.send_message(
        message.chat.id,
        "⚠️ Tasdiqlash\n\n"
        "Ushbu xabar barcha foydalanuvchilarga yuboriladi.\n"
        "Davom etishni xohlaysizmi?",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == "broadcast_confirm")
def broadcast_confirm(call):
    """Broadcast tasdiqlash"""
    admin_id = call.from_user.id
    
    if admin_id not in broadcast_sessions:
        bot.answer_callback_query(call.id, "❌ Sessiya tugagan!")
        return
    
    bot.answer_callback_query(call.id, "⏳ Yuborilmoqda...")
    bot.send_message(call.message.chat.id, "⏳ Xabar yuborilmoqda...\nBir oz kuting!")
    
    session = broadcast_sessions[admin_id]
    msg = session['message']
    
    # Barcha foydalanuvchilarga yuborish
    user_ids = asyncio.run(get_all_user_ids())
    
    success = 0
    failed = 0
    blocked = 0
    
    for user_id in user_ids:
        try:
            # Xabar turini aniqlash va yuborish
            if msg.text:
                bot.send_message(user_id, msg.text)
            elif msg.photo:
                bot.send_photo(user_id, msg.photo[-1].file_id, caption=msg.caption)
            elif msg.video:
                bot.send_video(user_id, msg.video.file_id, caption=msg.caption)
            elif msg.document:
                bot.send_document(user_id, msg.document.file_id, caption=msg.caption)
            elif msg.sticker:
                bot.send_sticker(user_id, msg.sticker.file_id)
            
            success += 1
            
        except Exception as e:
            if "blocked" in str(e).lower():
                blocked += 1
            else:
                failed += 1
    
    # Natijani ko'rsatish
    total = len(user_ids)
    
    result_text = (
        f"✅ Xabar yuborish yakunlandi!\n\n"
        f"📊 Natijalar:\n"
        f"👥 Jami: {total}\n"
        f"✅ Yuborildi: {success}\n"
        f"🚫 Blok qilgan: {blocked}\n"
        f"❌ Xato: {failed}"
    )
    
    bot.send_message(call.message.chat.id, result_text)
    
    del broadcast_sessions[admin_id]
    broadcast_menu(call.message)


@bot.callback_query_handler(func=lambda call: call.data == "broadcast_cancel")
def broadcast_cancel(call):
    """Broadcast bekor qilish"""
    admin_id = call.from_user.id
    
    if admin_id in broadcast_sessions:
        del broadcast_sessions[admin_id]
    
    bot.answer_callback_query(call.id, "❌ Bekor qilindi")
    bot.send_message(call.message.chat.id, "❌ Xabar yuborish bekor qilindi.")
    broadcast_menu(call.message)


# ==================== ORQAGA TUGMASI ====================

@bot.message_handler(func=lambda m: m.text == "🔙 Admin Panelga" and m.from_user.id == ADMIN_ID)
def back_to_admin_panel(message):
    """Admin panelga qaytish"""
    if message.from_user.id in broadcast_sessions:
        del broadcast_sessions[message.from_user.id]
    admin_panel(message)


# ==================== BEKOR QILISH ====================

@bot.message_handler(func=lambda m: m.text == "❌ Bekor qilish" and m.from_user.id == ADMIN_ID)
def cancel_broadcast(message):
    """Broadcast jarayonini bekor qilish"""
    if message.from_user.id in broadcast_sessions:
        del broadcast_sessions[message.from_user.id]
    bot.send_message(message.chat.id, "❌ Jarayon bekor qilindi.")
    broadcast_menu(message)

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.from_user.id in admin_sessions)
def admin_add_question_process(message):
    """Savol qo'shish jarayoni"""
    user_id = message.from_user.id
    session = admin_sessions[user_id]
    step = session['step']
    
    if step == 1:
        session['question'] = message.text
        session['step'] = 2
        bot.send_message(message.chat.id, "2️⃣ A variantini kiriting:")
    elif step == 2:
        session['option_a'] = message.text
        session['step'] = 3
        bot.send_message(message.chat.id, "3️⃣ B variantini kiriting:")
    elif step == 3:
        session['option_b'] = message.text
        session['step'] = 4
        bot.send_message(message.chat.id, "4️⃣ C variantini kiriting:")
    elif step == 4:
        session['option_c'] = message.text
        session['step'] = 5
        bot.send_message(message.chat.id, "5️⃣ D variantini kiriting:")
    elif step == 5:
        session['option_d'] = message.text
        session['step'] = 6
        bot.send_message(message.chat.id, "6️⃣ To'g'ri javobni kiriting (A, B, C yoki D):")
    elif step == 6:
        answer = message.text.upper()
        if answer in ['A', 'B', 'C', 'D']:
            session['correct_answer'] = answer
            session['step'] = 7
            bot.send_message(message.chat.id, "7️⃣ Izoh kiriting (yoki 'yo'q' deb yozing):")
        else:
            bot.send_message(message.chat.id, "❌ Faqat A, B, C yoki D harfini kiriting!")
    elif step == 7:
        explanation = None if message.text.lower() == "yo'q" else message.text
        
        asyncio.run(add_question(
            session['question'],
            session['option_a'],
            session['option_b'],
            session['option_c'],
            session['option_d'],
            session['correct_answer'],
            explanation
        ))
        
        bot.send_message(message.chat.id, "✅ Savol muvaffaqiyatli qo'shildi!")
        del admin_sessions[user_id]
        admin_panel(message)


# ╔══════════════════════════════════════════════════════════════╗
# ║                  🏆 TURNIR TIZIMI                           ║
# ╚══════════════════════════════════════════════════════════════╝

# ==================== TURNIR DATABASE JADVALLARI ====================

async def init_tournament_tables():
    """Turnir jadvallari"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Asosiy turnirlar jadvali
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tournaments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'upcoming',
                -- status: upcoming | registration | active | finished
                max_participants INTEGER DEFAULT 32,
                questions_per_match INTEGER DEFAULT 10,
                time_limit INTEGER DEFAULT 60,
                xp_reward_1 INTEGER DEFAULT 1000,
                xp_reward_2 INTEGER DEFAULT 500,
                xp_reward_3 INTEGER DEFAULT 250,
                registration_start TEXT,
                registration_end TEXT,
                tournament_start TEXT,
                tournament_end TEXT,
                created_by INTEGER,
                winner_id INTEGER,
                created_at TEXT
            )
        ''')

        # Turnir ishtirokchilari
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tournament_participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tournament_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                username TEXT,
                registered_at TEXT,
                is_eliminated INTEGER DEFAULT 0,
                current_round INTEGER DEFAULT 1,
                total_score INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                UNIQUE(tournament_id, user_id),
                FOREIGN KEY (tournament_id) REFERENCES tournaments(id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        # Turnir o'yinlari (matches)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tournament_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tournament_id INTEGER NOT NULL,
                round_number INTEGER NOT NULL,
                player1_id INTEGER NOT NULL,
                player2_id INTEGER,
                -- player2_id NULL = BYE (avtomatik o'tish)
                player1_score INTEGER DEFAULT 0,
                player2_score INTEGER DEFAULT 0,
                winner_id INTEGER,
                status TEXT DEFAULT 'pending',
                -- pending | active | finished
                started_at TEXT,
                finished_at TEXT,
                FOREIGN KEY (tournament_id) REFERENCES tournaments(id)
            )
        ''')

        # Turnir o'yin sessiyalari (real-time)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tournament_match_sessions (
                match_id INTEGER PRIMARY KEY,
                questions TEXT NOT NULL,
                player1_answers TEXT DEFAULT '{}',
                player2_answers TEXT DEFAULT '{}',
                player1_done INTEGER DEFAULT 0,
                player2_done INTEGER DEFAULT 0,
                FOREIGN KEY (match_id) REFERENCES tournament_matches(id)
            )
        ''')

        await db.commit()


# ==================== TURNIR DATABASE FUNKSIYALARI ====================

async def create_tournament(name, description, max_p, q_per_match, time_limit,
                            xp1, xp2, xp3, reg_start, reg_end, t_start, admin_id):
    """Yangi turnir yaratish"""
    async with aiosqlite.connect(DB_PATH) as db:
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = await db.execute('''
            INSERT INTO tournaments
            (name, description, status, max_participants, questions_per_match,
             time_limit, xp_reward_1, xp_reward_2, xp_reward_3,
             registration_start, registration_end, tournament_start,
             created_by, created_at)
            VALUES (?, ?, 'registration', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, description, max_p, q_per_match, time_limit,
              xp1, xp2, xp3, reg_start, reg_end, t_start, admin_id, now))
        await db.commit()
        return cursor.lastrowid


async def get_active_tournaments():
    """Faol va ro'yxatdan o'tish ochiq turnirlar"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT id, name, description, status, max_participants,
                   questions_per_match, time_limit,
                   xp_reward_1, xp_reward_2, xp_reward_3,
                   registration_start, registration_end, tournament_start
            FROM tournaments
            WHERE status IN ('upcoming', 'registration', 'active')
            ORDER BY id DESC
        ''')
        return await cursor.fetchall()


async def get_tournament_by_id(t_id):
    """Turnir ma'lumotlari"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT * FROM tournaments WHERE id = ?', (t_id,))
        return await cursor.fetchone()


async def get_all_tournaments(limit=10):
    """Barcha turnirlar (oxirgilardan)"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT id, name, status, max_participants, tournament_start, winner_id '
            'FROM tournaments ORDER BY id DESC LIMIT ?', (limit,))
        return await cursor.fetchall()


async def register_for_tournament(t_id, user_id, username):
    """Turnirga ro'yxatdan o'tish"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Turnir mavjudmi va ochiqmi
        cursor = await db.execute(
            'SELECT status, max_participants FROM tournaments WHERE id = ?', (t_id,))
        t = await cursor.fetchone()
        if not t:
            return False, "Turnir topilmadi"
        if t[0] != 'registration':
            return False, "Ro'yxatdan o'tish yopiq"

        # Ishtirokchilar soni
        cursor = await db.execute(
            'SELECT COUNT(*) FROM tournament_participants WHERE tournament_id = ?', (t_id,))
        count = (await cursor.fetchone())[0]
        if count >= t[1]:
            return False, f"Turnir to'lgan ({t[1]}/{t[1]})"

        # Allaqachon ro'yxatdan o'tganmi
        cursor = await db.execute(
            'SELECT id FROM tournament_participants WHERE tournament_id=? AND user_id=?',
            (t_id, user_id))
        if await cursor.fetchone():
            return False, "Siz allaqachon ro'yxatdan o'tgansiz"

        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await db.execute(
            'INSERT INTO tournament_participants (tournament_id, user_id, username, registered_at) '
            'VALUES (?, ?, ?, ?)', (t_id, user_id, username, now))
        await db.commit()
        return True, "Muvaffaqiyatli ro'yxatdan o'tdingiz"


async def get_tournament_participants(t_id):
    """Turnir ishtirokchilari"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT tp.user_id, tp.username, tp.total_score, tp.wins,
                   tp.losses, tp.current_round, tp.is_eliminated
            FROM tournament_participants tp
            WHERE tp.tournament_id = ?
            ORDER BY tp.total_score DESC, tp.wins DESC
        ''', (t_id,))
        return await cursor.fetchall()


async def get_participant_count(t_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT COUNT(*) FROM tournament_participants WHERE tournament_id = ?', (t_id,))
        return (await cursor.fetchone())[0]


async def is_registered(t_id, user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT id FROM tournament_participants WHERE tournament_id=? AND user_id=?',
            (t_id, user_id))
        return await cursor.fetchone() is not None


async def start_tournament(t_id):
    """Turnirni boshlash va birinchi raundni yaratish"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Statusni active ga o'tkazish
        await db.execute(
            "UPDATE tournaments SET status='active' WHERE id=?", (t_id,))

        # Ishtirokchilarni olish (tasodifiy tartibda)
        cursor = await db.execute(
            'SELECT user_id FROM tournament_participants WHERE tournament_id=? AND is_eliminated=0',
            (t_id,))
        players = [r[0] for r in await cursor.fetchall()]
        import random
        random.shuffle(players)

        # Juftlik yaratish
        matches_created = 0
        for i in range(0, len(players), 2):
            p1 = players[i]
            p2 = players[i+1] if i+1 < len(players) else None
            await db.execute(
                'INSERT INTO tournament_matches (tournament_id, round_number, player1_id, player2_id, status) '
                'VALUES (?, 1, ?, ?, ?)',
                (t_id, p1, p2, 'pending' if p2 else 'finished'))
            # BYE bo'lsa avtomatik o'tish
            if p2 is None:
                await db.execute(
                    'UPDATE tournament_matches SET winner_id=?, status="finished" '
                    'WHERE tournament_id=? AND round_number=1 AND player1_id=?',
                    (p1, t_id, p1))
            matches_created += 1

        await db.commit()
        return matches_created


async def get_pending_matches(t_id, round_num=None):
    """Kutayotgan matchlar"""
    async with aiosqlite.connect(DB_PATH) as db:
        if round_num:
            cursor = await db.execute(
                "SELECT id, player1_id, player2_id, round_number FROM tournament_matches "
                "WHERE tournament_id=? AND round_number=? AND status='pending'",
                (t_id, round_num))
        else:
            cursor = await db.execute(
                "SELECT id, player1_id, player2_id, round_number FROM tournament_matches "
                "WHERE tournament_id=? AND status='pending'", (t_id,))
        return await cursor.fetchall()


async def get_current_round(t_id):
    """Hozirgi raund raqami"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT MAX(round_number) FROM tournament_matches WHERE tournament_id=?', (t_id,))
        r = await cursor.fetchone()
        return r[0] or 1


async def get_user_tournament_match(t_id, user_id):
    """Foydalanuvchining hozirgi matchi"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT id, player1_id, player2_id, round_number, status
            FROM tournament_matches
            WHERE tournament_id=?
            AND (player1_id=? OR player2_id=?)
            AND status IN ('pending', 'active')
            ORDER BY round_number DESC LIMIT 1
        ''', (t_id, user_id, user_id))
        return await cursor.fetchone()


async def finish_tournament_match(match_id, p1_score, p2_score, winner_id, loser_id, t_id):
    """Matchni yakunlash"""
    async with aiosqlite.connect(DB_PATH) as db:
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        await db.execute(
            "UPDATE tournament_matches SET player1_score=?, player2_score=?, winner_id=?, "
            "status='finished', finished_at=? WHERE id=?",
            (p1_score, p2_score, winner_id, now, match_id))

        # G'olib statistikasini yangilash
        await db.execute(
            "UPDATE tournament_participants SET wins=wins+1, total_score=total_score+? "
            "WHERE tournament_id=? AND user_id=?", (p1_score if winner_id == loser_id else p2_score, t_id, winner_id))

        # Mag'lub bo'lgan o'yinchi eliminatsiya
        if loser_id:
            await db.execute(
                "UPDATE tournament_participants SET losses=losses+1, is_eliminated=1 "
                "WHERE tournament_id=? AND user_id=?", (t_id, loser_id))

        await db.commit()


async def check_round_finished(t_id, round_num):
    """Raund tugaganmi tekshirish"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM tournament_matches "
            "WHERE tournament_id=? AND round_number=? AND status != 'finished'",
            (t_id, round_num))
        return (await cursor.fetchone())[0] == 0


async def create_next_round(t_id, round_num):
    """Keyingi raundni yaratish"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Hozirgi raund g'oliblari
        cursor = await db.execute(
            "SELECT winner_id FROM tournament_matches "
            "WHERE tournament_id=? AND round_number=?", (t_id, round_num))
        winners = [r[0] for r in await cursor.fetchall() if r[0]]

        if len(winners) <= 1:
            # Final tugadi — g'olib topildi
            if winners:
                await db.execute(
                    "UPDATE tournaments SET status='finished', winner_id=? WHERE id=?",
                    (winners[0], t_id))
            await db.commit()
            return False, winners[0] if winners else None

        import random
        random.shuffle(winners)
        next_round = round_num + 1

        for i in range(0, len(winners), 2):
            p1 = winners[i]
            p2 = winners[i+1] if i+1 < len(winners) else None
            await db.execute(
                "INSERT INTO tournament_matches (tournament_id, round_number, player1_id, player2_id, status) "
                "VALUES (?, ?, ?, ?, ?)",
                (t_id, next_round, p1, p2, 'pending' if p2 else 'finished'))
            if p2 is None:
                await db.execute(
                    "UPDATE tournament_matches SET winner_id=?, status='finished' "
                    "WHERE tournament_id=? AND round_number=? AND player1_id=?",
                    (p1, t_id, next_round, p1))

        await db.commit()
        return True, None


async def get_tournament_bracket(t_id):
    """Turnir bracket — barcha matchlar"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT m.round_number, m.player1_id, m.player2_id,
                   m.player1_score, m.player2_score, m.winner_id, m.status,
                   u1.username as p1_name, u2.username as p2_name
            FROM tournament_matches m
            LEFT JOIN users u1 ON m.player1_id = u1.user_id
            LEFT JOIN users u2 ON m.player2_id = u2.user_id
            WHERE m.tournament_id = ?
            ORDER BY m.round_number ASC, m.id ASC
        ''', (t_id,))
        return await cursor.fetchall()


async def get_tournament_winners(t_id):
    """Top 3 ishtirokchi"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT tp.user_id, tp.username, tp.wins, tp.total_score
            FROM tournament_participants tp
            WHERE tp.tournament_id = ?
            ORDER BY tp.wins DESC, tp.total_score DESC
            LIMIT 3
        ''', (t_id,))
        return await cursor.fetchall()


async def get_user_tournament_history(user_id, limit=5):
    """Foydalanuvchining turnir tarixi"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT t.name, t.status, tp.wins, tp.losses,
                   tp.total_score, tp.is_eliminated,
                   CASE WHEN t.winner_id = tp.user_id THEN 1 ELSE 0 END as is_winner
            FROM tournament_participants tp
            JOIN tournaments t ON tp.tournament_id = t.id
            WHERE tp.user_id = ?
            ORDER BY t.id DESC LIMIT ?
        ''', (user_id, limit))
        return await cursor.fetchall()


# Turnir sessiyalari (xotira)
tournament_match_sessions = {}
# {match_id: {p1_id, p2_id, questions, p1_answers:{}, p2_answers:{}, p1_done, p2_done, tournament_id}}

admin_tournament_sessions = {}
# {admin_id: {step, data...}}


# ==================== FOYDALANUVCHI — TURNIR MENYUSI ====================

@bot.message_handler(func=lambda m: m.text == "🏆 Turnir")
def tournament_menu(message):
    """Turnir asosiy menyusi"""
    user_id = message.from_user.id

    tournaments = asyncio.run(get_active_tournaments())

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📋 Turnirlar ro'yxati", "🎯 Mening o'yinlarim")
    markup.row("📊 Turnir reytingi", "🏅 Mening tarixim")
    markup.row("🔙 Orqaga")

    active_count = len(tournaments)
    status_text = f"🔥 Hozir {active_count} ta faol turnir bor!" if active_count else "😴 Hozircha faol turnir yo'q."

    bot.send_message(
        message.chat.id,
        f"🏆 TURNIR TIZIMI\n\n"
        f"{status_text}\n\n"
        f"💡 Turnirda qatnashib XP va unvon yuting!\n"
        f"🥇 1-o'rin: Katta XP mukofot\n"
        f"🥈 2-o'rin: O'rta XP mukofot\n"
        f"🥉 3-o'rin: Kichik XP mukofot\n\n"
        f"Kerakli bo'limni tanlang:",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text == "📋 Turnirlar ro'yxati")
def show_tournaments_list(message):
    """Faol turnirlar ro'yxati"""
    user_id = message.from_user.id
    tournaments = asyncio.run(get_active_tournaments())

    if not tournaments:
        bot.send_message(
            message.chat.id,
            "😴 Hozircha faol turnir yo'q.\n\n"
            "Admin tez orada yangi turnir e'lon qiladi! 🔔"
        )
        return

    for t in tournaments:
        (t_id, name, desc, status, max_p, q_count, time_limit,
         xp1, xp2, xp3, reg_start, reg_end, t_start) = t

        count = asyncio.run(get_participant_count(t_id))
        registered = asyncio.run(is_registered(t_id, user_id))

        status_map = {
            'upcoming': '🔜 Tez orada',
            'registration': '✅ Ro\'yxat ochiq',
            'active': '⚔️ Davom etmoqda',
            'finished': '🏁 Tugagan'
        }
        status_text = status_map.get(status, status)

        text = (
            f"🏆 {name}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"📝 {desc or 'Tavsif yo\'q'}\n\n"
            f"🔄 Status: {status_text}\n"
            f"👥 Ishtirokchilar: {count}/{max_p}\n"
            f"❓ Har matchda: {q_count} savol\n"
            f"⏱ Vaqt: {time_limit} soniya\n\n"
            f"🎁 Mukofotlar:\n"
            f"🥇 1-o'rin: +{xp1:,} XP\n"
            f"🥈 2-o'rin: +{xp2:,} XP\n"
            f"🥉 3-o'rin: +{xp3:,} XP\n"
        )
        if reg_start:
            text += f"\n📅 Ro'yxat: {reg_start[:10]} — {reg_end[:10]}\n"
        if t_start:
            text += f"🚀 Boshlanish: {t_start[:16]}\n"

        markup = types.InlineKeyboardMarkup()
        if status == 'registration' and not registered:
            markup.add(types.InlineKeyboardButton(
                "✅ Ro'yxatdan o'tish", callback_data=f"t_register_{t_id}"))
        elif registered and status == 'registration':
            markup.add(types.InlineKeyboardButton(
                "✅ Ro'yxatdan o'tgansiz", callback_data="already_registered"))
        elif status == 'active' and registered:
            markup.add(types.InlineKeyboardButton(
                "⚔️ O'yinga kirish", callback_data=f"t_play_{t_id}"))
        markup.add(types.InlineKeyboardButton(
            "📊 Bracket ko'rish", callback_data=f"t_bracket_{t_id}"))

        bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('t_register_'))
def tournament_register_callback(call):
    """Turnirga ro'yxatdan o'tish"""
    user_id = call.from_user.id
    t_id = int(call.data.split('_')[2])
    username = call.from_user.username or call.from_user.first_name

    success, msg = asyncio.run(register_for_tournament(t_id, user_id, username))

    if success:
        bot.answer_callback_query(call.id, "✅ Ro'yxatdan o'tdingiz!")
        count = asyncio.run(get_participant_count(t_id))
        t = asyncio.run(get_tournament_by_id(t_id))
        bot.send_message(
            call.message.chat.id,
            f"🎉 RO'YXATDAN O'TDINGIZ!\n\n"
            f"🏆 Turnir: {t[1]}\n"
            f"👥 Siz {count}-ishtirokchisiz\n\n"
            f"Turnir boshlanishi haqida xabar beramiz! 🔔"
        )
    else:
        bot.answer_callback_query(call.id, f"❌ {msg}", show_alert=True)


@bot.callback_query_handler(func=lambda call: call.data == "already_registered")
def already_registered_cb(call):
    bot.answer_callback_query(call.id, "✅ Siz allaqachon ro'yxatdan o'tgansiz!", show_alert=True)


@bot.callback_query_handler(func=lambda call: call.data.startswith('t_bracket_'))
def show_bracket_callback(call):
    """Bracket ko'rsatish"""
    t_id = int(call.data.split('_')[2])
    bracket = asyncio.run(get_tournament_bracket(t_id))
    t = asyncio.run(get_tournament_by_id(t_id))

    if not bracket:
        bot.answer_callback_query(call.id, "📊 Hali matchlar yo'q!")
        return

    bot.answer_callback_query(call.id)

    text = f"📊 {t[1]} — BRACKET\n"
    text += "━━━━━━━━━━━━━━━━━━━\n\n"

    current_round = None
    for (rnd, p1_id, p2_id, s1, s2, winner, status, p1_name, p2_name) in bracket:
        if rnd != current_round:
            current_round = rnd
            text += f"\n🔄 RAUND {rnd}:\n"

        p1_display = f"@{p1_name}" if p1_name else f"ID:{p1_id}"
        if p2_id:
            p2_display = f"@{p2_name}" if p2_name else f"ID:{p2_id}"
        else:
            p2_display = "BYE"

        if status == 'finished' and winner:
            w_name = p1_display if winner == p1_id else p2_display
            text += f"✅ {p1_display} {s1}-{s2} {p2_display} → {w_name}\n"
        elif status == 'active':
            text += f"⚔️ {p1_display} vs {p2_display} (davom etmoqda)\n"
        else:
            text += f"⏳ {p1_display} vs {p2_display}\n"

    if len(text) > 4000:
        parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for part in parts:
            bot.send_message(call.message.chat.id, part)
    else:
        bot.send_message(call.message.chat.id, text)


@bot.callback_query_handler(func=lambda call: call.data.startswith('t_play_'))
def tournament_play_callback(call):
    """Turnirda o'ynash"""
    user_id = call.from_user.id
    t_id = int(call.data.split('_')[2])

    bot.answer_callback_query(call.id)

    # Foydalanuvchining hozirgi matchi
    match = asyncio.run(get_user_tournament_match(t_id, user_id))

    if not match:
        bot.send_message(
            call.message.chat.id,
            "⏳ Sizning matchingiz hali belgilanmagan yoki tugagan.\n"
            "Admin matchni boshlashini kuting!"
        )
        return

    match_id, p1_id, p2_id, round_num, status = match

    if status == 'active' and match_id in tournament_match_sessions:
        # O'yin davom etmoqda — savollarni ko'rsatish
        send_tournament_question(call.message.chat.id, user_id, match_id)
    elif status == 'pending':
        bot.send_message(
            call.message.chat.id,
            f"⏳ {round_num}-raund, matchingiz tayyorlanmoqda.\n"
            "Raqib tayyor bo'lgach o'yin boshlanadi! ⚔️"
        )
    else:
        bot.send_message(
            call.message.chat.id,
            "✅ Matchingiz tugagan yoki yangi raundni kuting."
        )


@bot.message_handler(func=lambda m: m.text == "🎯 Mening o'yinlarim")
def my_tournament_matches(message):
    """Foydalanuvchining aktiv matchlari"""
    user_id = message.from_user.id

    active_t = asyncio.run(get_active_tournaments())

    found = False
    for t in active_t:
        t_id = t[0]
        if not asyncio.run(is_registered(t_id, user_id)):
            continue
        match = asyncio.run(get_user_tournament_match(t_id, user_id))
        if match:
            found = True
            match_id, p1_id, p2_id, round_num, status = match

            opp_id = p2_id if p1_id == user_id else p1_id
            try:
                opp = bot.get_chat(opp_id)
                opp_name = f"@{opp.username}" if opp.username else opp.first_name
            except Exception:
                opp_name = f"ID:{opp_id}"

            status_text = "⚔️ Davom etmoqda" if status == 'active' else "⏳ Kutilmoqda"

            markup = types.InlineKeyboardMarkup()
            if status == 'active':
                markup.add(types.InlineKeyboardButton(
                    "🎯 O'ynash", callback_data=f"t_play_{t_id}"))

            bot.send_message(
                message.chat.id,
                f"🏆 {t[1]}\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"🔄 Raund: {round_num}\n"
                f"👤 Raqib: {opp_name}\n"
                f"📊 Status: {status_text}\n",
                reply_markup=markup
            )

    if not found:
        bot.send_message(
            message.chat.id,
            "😴 Hozircha aktiv matchingiz yo'q.\n"
            "Turnirga ro'yxatdan o'ting! 🏆"
        )


@bot.message_handler(func=lambda m: m.text == "🏅 Mening tarixim")
def my_tournament_history(message):
    """Foydalanuvchining turnir tarixi"""
    user_id = message.from_user.id
    history = asyncio.run(get_user_tournament_history(user_id))

    if not history:
        bot.send_message(
            message.chat.id,
            "😴 Hali hech qanday turnirda qatnashmadingiz.\n"
            "Birinchi turnirga ro'yxatdan o'ting! 🏆"
        )
        return

    text = "🏅 TURNIR TARIXINGIZ\n"
    text += "━━━━━━━━━━━━━━━━━━━\n\n"

    for (t_name, t_status, wins, losses, score, eliminated, is_winner) in history:
        if is_winner:
            place_icon = "🥇 G'OLIB"
        elif not eliminated:
            place_icon = "🎖 Ishtirok etdi"
        else:
            place_icon = f"🚫 {wins+losses}-raundda chiqdi"

        text += (
            f"🏆 {t_name}\n"
            f"  {place_icon}\n"
            f"  ✅ G'alaba: {wins} | ❌ Mag'lub: {losses}\n"
            f"  ⭐ Ball: {score}\n\n"
        )

    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: m.text == "📊 Turnir reytingi")
def tournament_overall_rating(message):
    """Eng ko'p turnir g'oliblari"""
    async def get_rating():
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute('''
                SELECT u.username, COUNT(*) as wins,
                       SUM(tp.wins) as match_wins,
                       SUM(tp.total_score) as total_xp
                FROM tournament_participants tp
                JOIN users u ON tp.user_id = u.user_id
                JOIN tournaments t ON tp.tournament_id = t.id
                WHERE t.winner_id = tp.user_id
                GROUP BY tp.user_id
                ORDER BY wins DESC, match_wins DESC
                LIMIT 10
            ''')
            return await cursor.fetchall()

    rating = asyncio.run(get_rating())

    if not rating:
        bot.send_message(message.chat.id, "📊 Hali tugagan turnirlar yo'q!")
        return

    text = "🏆 TURNIR REYTINGI\n"
    text += "Eng ko'p turnir g'oliblari\n"
    text += "━━━━━━━━━━━━━━━━━━━\n\n"

    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    for i, (username, t_wins, m_wins, total_xp) in enumerate(rating, 1):
        medal = medals.get(i, f"{i}.")
        text += (
            f"{medal} @{username if username else 'Anonim'}\n"
            f"   🏆 Turnir g'alabasi: {t_wins}\n"
            f"   ⚔️ Match g'alabasi: {m_wins}\n"
            f"   ⭐ Jami XP: {total_xp:,}\n\n"
        )

    bot.send_message(message.chat.id, text)


# ==================== TURNIR O'YIN LOGIKASI ====================

def start_tournament_match(match_id, p1_id, p2_id, t_id, q_count=10):
    """Match o'yinini boshlash"""
    questions = asyncio.run(get_random_questions(q_count))

    if len(questions) < q_count:
        bot.send_message(p1_id, "❌ Savollar yetarli emas! Admin bilan bog'laning.")
        bot.send_message(p2_id, "❌ Savollar yetarli emas! Admin bilan bog'laning.")
        return

    tournament_match_sessions[match_id] = {
        'tournament_id': t_id,
        'p1_id': p1_id,
        'p2_id': p2_id,
        'questions': questions,
        'p1_answers': {},
        'p2_answers': {},
        'p1_current': 0,
        'p2_current': 0,
        'p1_score': 0,
        'p2_score': 0,
        'p1_done': False,
        'p2_done': False,
        'total_q': q_count
    }

    # Raqib ismlarini olish
    try:
        p1_name = f"@{bot.get_chat(p1_id).username}" or bot.get_chat(p1_id).first_name
    except Exception:
        p1_name = f"ID:{p1_id}"
    try:
        p2_name = f"@{bot.get_chat(p2_id).username}" or bot.get_chat(p2_id).first_name
    except Exception:
        p2_name = f"ID:{p2_id}"

    import time

    bot.send_message(
        p1_id,
        f"⚔️ TURNIR MATCHI BOSHLANDI!\n\n"
        f"🆚 Raqibingiz: {p2_name}\n"
        f"❓ {q_count} ta savol\n"
        f"🏆 G'olib turnirda davom etadi!\n\n"
        f"3... 2... 1... BOSHLANG! 🚀"
    )
    bot.send_message(
        p2_id,
        f"⚔️ TURNIR MATCHI BOSHLANDI!\n\n"
        f"🆚 Raqibingiz: {p1_name}\n"
        f"❓ {q_count} ta savol\n"
        f"🏆 G'olib turnirda davom etadi!\n\n"
        f"3... 2... 1... BOSHLANG! 🚀"
    )

    time.sleep(2)
    send_tournament_question(None, p1_id, match_id)
    send_tournament_question(None, p2_id, match_id)


def send_tournament_question(chat_id, user_id, match_id):
    """Turnir savolini yuborish"""
    if match_id not in tournament_match_sessions:
        return

    session = tournament_match_sessions[match_id]
    is_p1 = (user_id == session['p1_id'])
    current_key = 'p1_current' if is_p1 else 'p2_current'
    done_key = 'p1_done' if is_p1 else 'p2_done'

    current = session[current_key]
    send_to = chat_id or user_id

    if current >= session['total_q']:
        session[done_key] = True
        check_tournament_match_finish(match_id)
        return

    q = session['questions'][current]
    q_id, question, opt_a, opt_b, opt_c, opt_d, correct, explanation = q

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(f"A) {opt_a}", callback_data=f"tm_{match_id}_{current}_A"),
        types.InlineKeyboardButton(f"B) {opt_b}", callback_data=f"tm_{match_id}_{current}_B"),
    )
    markup.row(
        types.InlineKeyboardButton(f"C) {opt_c}", callback_data=f"tm_{match_id}_{current}_C"),
        types.InlineKeyboardButton(f"D) {opt_d}", callback_data=f"tm_{match_id}_{current}_D"),
    )

    score_key = 'p1_score' if is_p1 else 'p2_score'
    bot.send_message(
        send_to,
        f"⚔️ Savol {current+1}/{session['total_q']}\n"
        f"⭐ Hozirgi ball: {session[score_key]}\n\n"
        f"{question}\n\n"
        f"A) {opt_a}\n"
        f"B) {opt_b}\n"
        f"C) {opt_c}\n"
        f"D) {opt_d}",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('tm_'))
def tournament_match_answer(call):
    """Turnir matchi javobini qayta ishlash"""
    parts = call.data.split('_')
    match_id = int(parts[1])
    q_index = int(parts[2])
    user_answer = parts[3]
    user_id = call.from_user.id

    if match_id not in tournament_match_sessions:
        bot.answer_callback_query(call.id, "❌ Match tugagan!")
        return

    session = tournament_match_sessions[match_id]
    is_p1 = (user_id == session['p1_id'])

    if not (user_id == session['p1_id'] or user_id == session['p2_id']):
        bot.answer_callback_query(call.id, "❌ Bu sizning matchingiz emas!")
        return

    current_key = 'p1_current' if is_p1 else 'p2_current'
    score_key = 'p1_score' if is_p1 else 'p2_score'
    done_key = 'p1_done' if is_p1 else 'p2_done'
    answers_key = 'p1_answers' if is_p1 else 'p2_answers'

    # Allaqachon javob berganmi
    if session[done_key] or session[current_key] != q_index:
        bot.answer_callback_query(call.id, "⏭ Bu savol o'tgan!")
        return

    # Javobni tekshirish
    q = session['questions'][q_index]
    correct = q[6]
    is_correct = (user_answer == correct)

    session[answers_key][q_index] = user_answer
    if is_correct:
        session[score_key] += 1
        bot.answer_callback_query(call.id, "✅ To'g'ri!")
    else:
        bot.answer_callback_query(call.id, f"❌ Noto'g'ri! To'g'ri: {correct}")

    session[current_key] += 1

    # Keyingi savolga o'tish
    if session[current_key] >= session['total_q']:
        session[done_key] = True
        bot.send_message(
            user_id,
            f"✅ Siz barcha savollarni yechdingiz!\n"
            f"⭐ Natijangiz: {session[score_key]}/{session['total_q']}\n\n"
            f"⏳ Raqibingiz tugashini kuting..."
        )
        check_tournament_match_finish(match_id)
    else:
        send_tournament_question(user_id, user_id, match_id)


def check_tournament_match_finish(match_id):
    """Ikkala o'yinchi ham tugaganmi tekshirish"""
    if match_id not in tournament_match_sessions:
        return

    session = tournament_match_sessions[match_id]

    if not (session['p1_done'] and session['p2_done']):
        return  # Biri hali tugamagan

    p1_id = session['p1_id']
    p2_id = session['p2_id']
    p1_score = session['p1_score']
    p2_score = session['p2_score']
    t_id = session['tournament_id']
    total_q = session['total_q']

    # G'olibni aniqlash
    if p1_score > p2_score:
        winner_id, loser_id = p1_id, p2_id
        result = "🏆 G'OLDINGIZ!"
        loser_result = "😔 Yutqazdingiz!"
    elif p2_score > p1_score:
        winner_id, loser_id = p2_id, p1_id
        result = "😔 Yutqazdingiz!"
        loser_result = "🏆 G'OLDINGIZ!"
    else:
        # Teng — random
        import random
        winner_id = random.choice([p1_id, p2_id])
        loser_id = p2_id if winner_id == p1_id else p1_id
        result = "🏆 G'OLDINGIZ! (teng natijada tasodifiy)" if winner_id == p1_id else "😔 Yutqazdingiz! (teng, tasodifiy)"
        loser_result = "🏆 G'OLDINGIZ! (teng natijada tasodifiy)" if winner_id == p2_id else "😔 Yutqazdingiz! (teng, tasodifiy)"

    # Natijani ko'rsatish
    try:
        w_name = f"@{bot.get_chat(winner_id).username}" or str(winner_id)
    except Exception:
        w_name = str(winner_id)

    w_is_p1 = (winner_id == p1_id)
    w_score = p1_score if w_is_p1 else p2_score
    l_score = p2_score if w_is_p1 else p1_score

    p1_result_text = result if p1_id == winner_id else loser_result
    p2_result_text = result if p2_id == winner_id else loser_result

    bot.send_message(
        p1_id,
        f"{'⚔️' } MATCH NATIJASI\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"{p1_result_text}\n\n"
        f"📊 Natija: {p1_score} — {p2_score}\n"
        f"🏆 G'olib: {w_name} ({w_score}/{total_q})\n\n"
        f"{'🚀 Keyingi raundda kuring!' if p1_id==winner_id else '📚 Ko\'proq mashq qiling!'}"
    )
    bot.send_message(
        p2_id,
        f"⚔️ MATCH NATIJASI\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"{p2_result_text}\n\n"
        f"📊 Natija: {p2_score} — {p1_score}\n"
        f"🏆 G'olib: {w_name} ({w_score}/{total_q})\n\n"
        f"{'🚀 Keyingi raundda kuring!' if p2_id==winner_id else '📚 Ko\'proq mashq qiling!'}"
    )

    # DB ga saqlash
    asyncio.run(finish_tournament_match(match_id, p1_score, p2_score, winner_id, loser_id, t_id))

    # Sessiyani tozalash
    del tournament_match_sessions[match_id]

    # Raund tugadimi tekshirish
    cur_round = asyncio.run(get_current_round(t_id))
    round_done = asyncio.run(check_round_finished(t_id, cur_round))

    if round_done:
        has_next, final_winner_id = asyncio.run(create_next_round(t_id, cur_round))
        if has_next:
            # Yangi raund boshlandi — barcha ishtirokchilarga xabar
            participants = asyncio.run(get_tournament_participants(t_id))
            t = asyncio.run(get_tournament_by_id(t_id))
            for (uid, uname, *_) in participants:
                if not _[4]:  # is_eliminated = False
                    try:
                        match = asyncio.run(get_user_tournament_match(t_id, uid))
                        if match:
                            opp_id = match[2] if match[1] == uid else match[1]
                            try:
                                opp_name = f"@{bot.get_chat(opp_id).username}" or str(opp_id)
                            except Exception:
                                opp_name = str(opp_id)
                            markup = types.InlineKeyboardMarkup()
                            markup.add(types.InlineKeyboardButton(
                                "⚔️ O'ynash", callback_data=f"t_play_{t_id}"))
                            bot.send_message(
                                uid,
                                f"🔄 {cur_round+1}-RAUND BOSHLANDI!\n\n"
                                f"🏆 Turnir: {t[1]}\n"
                                f"👤 Raqibingiz: {opp_name}\n\n"
                                f"Tayyor bo'lsangiz boshlang! 👇",
                                reply_markup=markup
                            )
                    except Exception:
                        pass
        else:
            # Turnir tugadi
            if final_winner_id:
                t = asyncio.run(get_tournament_by_id(t_id))
                winners = asyncio.run(get_tournament_winners(t_id))
                xp_rewards = [t[7], t[8], t[9]]  # xp1, xp2, xp3

                # XP berish va xabar yuborish
                for i, (w_uid, w_uname, w_wins, w_score) in enumerate(winners):
                    place = i + 1
                    place_icon = ["🥇", "🥈", "🥉"][i]
                    xp_reward = xp_rewards[i] if i < len(xp_rewards) else 0
                    asyncio.run(update_user_xp(w_uid, xp_reward))
                    try:
                        bot.send_message(
                            w_uid,
                            f"🎉 TURNIR YAKUNLANDI!\n\n"
                            f"🏆 {t[1]}\n"
                            f"{place_icon} Siz {place}-o'rinni egalladingiz!\n\n"
                            f"🏅 {w_wins} ta match g'alabasi\n"
                            f"⭐ XP mukofot: +{xp_reward:,}\n\n"
                            f"Tabriklaymiz! 🎊"
                        )
                    except Exception:
                        pass

                # Umumiy e'lon
                try:
                    w_user = bot.get_chat(final_winner_id)
                    w_display = f"@{w_user.username}" if w_user.username else w_user.first_name
                except Exception:
                    w_display = str(final_winner_id)

                announce = (
                    f"🏆 TURNIR YAKUNLANDI!\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"🎊 {t[1]}\n\n"
                    f"🥇 G'OLIB: {w_display}\n\n"
                )
                if len(winners) > 1:
                    for i, (_, uname, wins, score) in enumerate(winners[:3]):
                        place_icon = ["🥇", "🥈", "🥉"][i]
                        announce += f"{place_icon} @{uname if uname else 'Anonim'} — {wins} g'alaba\n"

                try:
                    bot.send_message(CHANNEL_USERNAME, announce)
                except Exception:
                    pass


# ==================== ADMIN — TURNIR BOSHQARUVI ====================

@bot.message_handler(func=lambda m: m.text == "🏆 Turnir Boshqaruvi" and m.from_user.id == ADMIN_ID)
def admin_tournament_menu(message):
    """Admin turnir menyusi"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("➕ Yangi Turnir", "📋 Barcha Turnirlar")
    markup.row("🚀 Turnir Boshlash", "⚔️ Match Boshlash")
    markup.row("📊 Turnir Statistikasi")
    markup.row("🔙 Admin Panelga")

    bot.send_message(
        message.chat.id,
        "🏆 TURNIR BOSHQARUVI\n\n"
        "Kerakli bo'limni tanlang:",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text == "➕ Yangi Turnir" and m.from_user.id == ADMIN_ID)
def create_tournament_start(message):
    """Yangi turnir yaratish"""
    admin_tournament_sessions[message.from_user.id] = {'step': 1, 'data': {}}

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("❌ Bekor qilish")

    bot.send_message(
        message.chat.id,
        "➕ YANGI TURNIR YARATISH\n\n"
        "1️⃣ Turnir nomini kiriting:\n"
        "(Masalan: Bahorgi Matematika Chempionati)",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and
                     m.from_user.id in admin_tournament_sessions)
def create_tournament_process(message):
    """Turnir yaratish jarayoni"""
    admin_id = message.from_user.id
    session = admin_tournament_sessions[admin_id]
    step = session['step']
    data = session['data']

    if message.text == "❌ Bekor qilish":
        del admin_tournament_sessions[admin_id]
        admin_tournament_menu(message)
        return

    if step == 1:
        data['name'] = message.text
        session['step'] = 2
        bot.send_message(message.chat.id,
            "2️⃣ Qisqacha tavsif kiriting:\n"
            "(Masalan: Barcha yoshdagilar uchun ochiq musobaqa)")

    elif step == 2:
        data['description'] = message.text
        session['step'] = 3
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("8", "16", "32")
        markup.row("❌ Bekor qilish")
        bot.send_message(message.chat.id,
            "3️⃣ Maksimal ishtirokchilar soni:\n"
            "(8, 16 yoki 32 — 2 darajasida bo'lishi kerak)",
            reply_markup=markup)

    elif step == 3:
        try:
            max_p = int(message.text)
            if max_p not in [4, 8, 16, 32, 64]:
                bot.send_message(message.chat.id, "❌ 8, 16 yoki 32 kiriting!")
                return
            data['max_participants'] = max_p
            session['step'] = 4
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row("5", "10", "15")
            markup.row("❌ Bekor qilish")
            bot.send_message(message.chat.id,
                "4️⃣ Har matchda nechta savol?\n(5, 10 yoki 15)",
                reply_markup=markup)
        except ValueError:
            bot.send_message(message.chat.id, "❌ Raqam kiriting!")

    elif step == 4:
        try:
            q_count = int(message.text)
            if q_count not in [5, 10, 15]:
                bot.send_message(message.chat.id, "❌ 5, 10 yoki 15 kiriting!")
                return
            data['q_per_match'] = q_count
            session['step'] = 5
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row("30", "60", "90")
            markup.row("❌ Bekor qilish")
            bot.send_message(message.chat.id,
                "5️⃣ Vaqt limiti (soniya, har match uchun):\n(30, 60 yoki 90)",
                reply_markup=markup)
        except ValueError:
            bot.send_message(message.chat.id, "❌ Raqam kiriting!")

    elif step == 5:
        try:
            data['time_limit'] = int(message.text)
            session['step'] = 6
            bot.send_message(message.chat.id,
                "6️⃣ 1-o'rin XP mukofoti:\n(Masalan: 2000)")
        except ValueError:
            bot.send_message(message.chat.id, "❌ Raqam kiriting!")

    elif step == 6:
        try:
            data['xp1'] = int(message.text)
            session['step'] = 7
            bot.send_message(message.chat.id,
                "7️⃣ 2-o'rin XP mukofoti:\n(Masalan: 1000)")
        except ValueError:
            bot.send_message(message.chat.id, "❌ Raqam kiriting!")

    elif step == 7:
        try:
            data['xp2'] = int(message.text)
            session['step'] = 8
            bot.send_message(message.chat.id,
                "8️⃣ 3-o'rin XP mukofoti:\n(Masalan: 500)")
        except ValueError:
            bot.send_message(message.chat.id, "❌ Raqam kiriting!")

    elif step == 8:
        try:
            data['xp3'] = int(message.text)
            session['step'] = 9
            from datetime import datetime
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            bot.send_message(message.chat.id,
                f"9️⃣ Ro'yxat tugash vaqti:\n"
                f"Format: YYYY-MM-DD HH:MM\n"
                f"Masalan: {now_str}")
        except ValueError:
            bot.send_message(message.chat.id, "❌ Raqam kiriting!")

    elif step == 9:
        data['reg_end'] = message.text
        session['step'] = 10
        bot.send_message(message.chat.id,
            "🔟 Turnir boshlanish vaqti:\n"
            "Format: YYYY-MM-DD HH:MM\n"
            "(Ro'yxat tugagandan keyin bo'lishi kerak)")

    elif step == 10:
        data['t_start'] = message.text

        # Tasdiqlash
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("✅ Yaratish", callback_data="confirm_create_tournament"),
            types.InlineKeyboardButton("❌ Bekor", callback_data="cancel_create_tournament")
        )

        summary = (
            f"📋 TURNIR MA'LUMOTLARI:\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"📛 Nom: {data['name']}\n"
            f"📝 Tavsif: {data['description']}\n"
            f"👥 Max ishtirokchi: {data['max_participants']}\n"
            f"❓ Savollar: {data['q_per_match']} ta\n"
            f"⏱ Vaqt: {data['time_limit']} soniya\n"
            f"🥇 XP 1: +{data['xp1']:,}\n"
            f"🥈 XP 2: +{data['xp2']:,}\n"
            f"🥉 XP 3: +{data['xp3']:,}\n"
            f"📅 Ro'yxat tugashi: {data['reg_end']}\n"
            f"🚀 Boshlanish: {data['t_start']}\n\n"
            f"Tasdiqlaysizmi?"
        )
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("✅ Tasdiqlash", "❌ Bekor qilish")
        session['step'] = 11
        bot.send_message(message.chat.id, summary, reply_markup=markup)

    elif step == 11:
        if message.text == "✅ Tasdiqlash":
            from datetime import datetime
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            t_id = asyncio.run(create_tournament(
                data['name'], data['description'],
                data['max_participants'], data['q_per_match'],
                data['time_limit'], data['xp1'], data['xp2'], data['xp3'],
                now, data['reg_end'], data['t_start'], admin_id
            ))
            del admin_tournament_sessions[admin_id]

            # Kanalga e'lon
            try:
                bot_me = bot.get_me()
                bot_link = f"https://t.me/{bot_me.username}?start=tournament"
                bot.send_message(
                    CHANNEL_USERNAME,
                    f"🏆 YANGI TURNIR E'LON QILINDI!\n\n"
                    f"📛 {data['name']}\n"
                    f"📝 {data['description']}\n\n"
                    f"👥 Max: {data['max_participants']} ishtirokchi\n"
                    f"🚀 Boshlanish: {data['t_start']}\n\n"
                    f"🥇 +{data['xp1']:,} XP\n"
                    f"🥈 +{data['xp2']:,} XP\n"
                    f"🥉 +{data['xp3']:,} XP\n\n"
                    f"👉 Ro'yxatdan o'tish: {bot_link}"
                )
            except Exception:
                pass

            bot.send_message(
                message.chat.id,
                f"✅ Turnir yaratildi! (ID: {t_id})\n"
                f"Kanalga e'lon yuborildi! 📢\n\n"
                f"Ishtirokchilar yig'ilgach '🚀 Turnir Boshlash' tugmasini bosing.",
                reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
            )
            admin_tournament_menu(message)
        else:
            del admin_tournament_sessions[admin_id]
            bot.send_message(message.chat.id, "❌ Bekor qilindi.")
            admin_tournament_menu(message)


@bot.message_handler(func=lambda m: m.text == "📋 Barcha Turnirlar" and m.from_user.id == ADMIN_ID)
def admin_list_tournaments(message):
    """Admin uchun barcha turnirlar"""
    tournaments = asyncio.run(get_all_tournaments(20))

    if not tournaments:
        bot.send_message(message.chat.id, "❌ Hali turnirlar yo'q!")
        return

    text = "📋 BARCHA TURNIRLAR\n━━━━━━━━━━━━━━━━━━━\n\n"
    status_map = {
        'upcoming': '🔜', 'registration': '✅',
        'active': '⚔️', 'finished': '🏁'
    }
    for (t_id, name, status, max_p, t_start, winner_id) in tournaments:
        count = asyncio.run(get_participant_count(t_id))
        icon = status_map.get(status, '❓')
        text += f"{icon} [{t_id}] {name}\n"
        text += f"   👥 {count}/{max_p} | 📅 {(t_start or 'N/A')[:10]}\n\n"

    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: m.text == "🚀 Turnir Boshlash" and m.from_user.id == ADMIN_ID)
def admin_start_tournament(message):
    """Turnirni boshlash"""
    tournaments = asyncio.run(get_all_tournaments())
    reg_open = [(t[0], t[1]) for t in tournaments if t[2] == 'registration']

    if not reg_open:
        bot.send_message(message.chat.id, "❌ Ro'yxat ochiq turnir yo'q!")
        return

    markup = types.InlineKeyboardMarkup()
    for t_id, name in reg_open:
        count = asyncio.run(get_participant_count(t_id))
        markup.add(types.InlineKeyboardButton(
            f"🚀 {name} ({count} kishi)", callback_data=f"admin_start_t_{t_id}"))

    bot.send_message(message.chat.id,
        "🚀 Qaysi turnirni boshlash?\n\n"
        "⚠️ Boshlash uchun kamida 2 ishtirokchi kerak!",
        reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_start_t_'))
def admin_start_tournament_cb(call):
    """Turnirni boshlash callback"""
    t_id = int(call.data.split('_')[3])
    bot.answer_callback_query(call.id, "⏳ Boshlashmoqda...")

    count = asyncio.run(get_participant_count(t_id))
    if count < 2:
        bot.send_message(call.message.chat.id, "❌ Kamida 2 ishtirokchi kerak!")
        return

    matches = asyncio.run(start_tournament(t_id))
    t = asyncio.run(get_tournament_by_id(t_id))

    bot.send_message(
        call.message.chat.id,
        f"✅ {t[1]} BOSHLANDI!\n\n"
        f"⚔️ 1-raund: {matches} ta match\n"
        f"👥 Ishtirokchilar: {count}\n\n"
        f"Endi '⚔️ Match Boshlash' tugmasi bilan matchlarni boshlang!"
    )

    # Barcha ishtirokchilarga xabar
    participants = asyncio.run(get_tournament_participants(t_id))
    for (uid, uname, *_) in participants:
        try:
            match = asyncio.run(get_user_tournament_match(t_id, uid))
            if match:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    "⚔️ O'yinga kirish", callback_data=f"t_play_{t_id}"))
                bot.send_message(
                    uid,
                    f"🏆 {t[1]} BOSHLANDI!\n\n"
                    f"⚔️ 1-raund matchi tayyorlandi!\n"
                    f"Admin matchni boshlagach o'ynaysiz. 👇",
                    reply_markup=markup
                )
        except Exception:
            pass


@bot.message_handler(func=lambda m: m.text == "⚔️ Match Boshlash" and m.from_user.id == ADMIN_ID)
def admin_start_match(message):
    """Matchni boshlash"""
    tournaments = asyncio.run(get_all_tournaments())
    active = [(t[0], t[1]) for t in tournaments if t[2] == 'active']

    if not active:
        bot.send_message(message.chat.id, "❌ Faol turnir yo'q!")
        return

    markup = types.InlineKeyboardMarkup()
    for t_id, name in active:
        cur_round = asyncio.run(get_current_round(t_id))
        pending = asyncio.run(get_pending_matches(t_id, cur_round))
        if pending:
            markup.add(types.InlineKeyboardButton(
                f"⚔️ {name} — {len(pending)} match kutmoqda",
                callback_data=f"admin_launch_matches_{t_id}"))

    if not markup.keyboard:
        bot.send_message(message.chat.id, "✅ Barcha matchlar allaqachon boshlangan!")
        return

    bot.send_message(message.chat.id, "⚔️ Qaysi turnir matchlarini boshlash?",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_launch_matches_'))
def admin_launch_matches_cb(call):
    """Raund matchlarini boshlash"""
    t_id = int(call.data.split('_')[3])
    bot.answer_callback_query(call.id, "⏳ Matchlar boshlanmoqda...")

    cur_round = asyncio.run(get_current_round(t_id))
    pending = asyncio.run(get_pending_matches(t_id, cur_round))
    t = asyncio.run(get_tournament_by_id(t_id))

    launched = 0
    for (match_id, p1_id, p2_id, rnd) in pending:
        if p2_id:
            # Matchni active qilish
            async def set_active(mid):
                async with aiosqlite.connect(DB_PATH) as db:
                    await db.execute(
                        "UPDATE tournament_matches SET status='active' WHERE id=?", (mid,))
                    await db.commit()
            asyncio.run(set_active(match_id))

            # O'yinni boshlash
            import threading
            t_thread = threading.Thread(
                target=start_tournament_match,
                args=(match_id, p1_id, p2_id, t_id, t[5])  # t[5] = questions_per_match
            )
            t_thread.daemon = True
            t_thread.start()
            launched += 1

    bot.send_message(
        call.message.chat.id,
        f"✅ {cur_round}-raund boshlandi!\n"
        f"⚔️ {launched} ta match ishga tushirildi!"
    )


@bot.message_handler(func=lambda m: m.text == "📊 Turnir Statistikasi" and m.from_user.id == ADMIN_ID)
def admin_tournament_stats(message):
    """Turnir statistikasi"""
    async def get_stats():
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM tournaments")
            total = (await cursor.fetchone())[0]
            cursor = await db.execute(
                "SELECT COUNT(*) FROM tournaments WHERE status='finished'")
            finished = (await cursor.fetchone())[0]
            cursor = await db.execute(
                "SELECT COUNT(*) FROM tournament_participants")
            total_reg = (await cursor.fetchone())[0]
            cursor = await db.execute(
                "SELECT COUNT(*) FROM tournament_matches WHERE status='finished'")
            total_matches = (await cursor.fetchone())[0]
            return total, finished, total_reg, total_matches

    total, finished, total_reg, total_matches = asyncio.run(get_stats())

    bot.send_message(
        message.chat.id,
        f"📊 TURNIR STATISTIKASI\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"🏆 Jami turnirlar: {total}\n"
        f"🏁 Tugagan: {finished}\n"
        f"⚔️ Faol: {total - finished}\n\n"
        f"👥 Jami ro'yxatlar: {total_reg}\n"
        f"⚔️ O'ynalgan matchlar: {total_matches}\n"
    )


# ==================== TURNIRNI INIT VA MENYUGA QO'SHISH ====================


# ╔══════════════════════════════════════════════════════════════╗
# ║                  💎 PREMIUM TIZIMI                          ║
# ╚══════════════════════════════════════════════════════════════╝

# ==================== PREMIUM SOZLAMALAR ====================

PREMIUM_PLANS = {
    'free': {
        'name': '🆓 Bepul',
        'quiz_limit': 200,        # Kunlik max savol
        'quiz_warning': 150,      # Ogohlantirish chegarasi
        'pvp_limit': 15,          # Kunlik PvP
        'xp_multiplier': 1,
        'price_som': 0,
        'price_stars': 0,
        'badge': '',
        'color': '',
    },
    'silver': {
        'name': '🥈 Silver',
        'quiz_limit': 99999,
        'pvp_limit': 99999,
        'xp_multiplier': 2,
        'price_som': 3000,
        'price_stars': 15,
        'badge': '🥈',
        'color': 'Kumush',
        'duration_days': 30,
    },
    'gold': {
        'name': '🥇 Gold',
        'quiz_limit': 99999,
        'pvp_limit': 99999,
        'xp_multiplier': 3,
        'price_som': 5000,
        'price_stars': 25,
        'badge': '🥇',
        'color': 'Oltin',
        'duration_days': 30,
        'free_tournament': True,
    },
    'diamond': {
        'name': '💎 Diamond',
        'quiz_limit': 99999,
        'pvp_limit': 99999,
        'xp_multiplier': 5,
        'price_som': 10000,
        'price_stars': 50,
        'badge': '💎',
        'color': 'Olmos',
        'duration_days': 30,
        'free_tournament': True,
        'custom_title': True,
    },
}

# Klan yaratish talablari (premiumsiz!)
CLAN_CREATE_REQUIREMENTS = {
    'min_level': 10,
    'xp_cost': 500,   # XP sarflanadi (balansdan ayriladi)
}


# ==================== PREMIUM DATABASE ====================

async def init_premium_tables():
    """Premium jadvallari"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Premium foydalanuvchilar
        await db.execute('''
            CREATE TABLE IF NOT EXISTS premium_users (
                user_id INTEGER PRIMARY KEY,
                plan TEXT DEFAULT 'free',
                started_at TEXT,
                expires_at TEXT,
                given_by TEXT DEFAULT 'purchase',
                -- purchase | admin | referral
                stars_paid INTEGER DEFAULT 0,
                som_paid INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        # Kunlik foydalanish hisobi
        await db.execute('''
            CREATE TABLE IF NOT EXISTS daily_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                quiz_count INTEGER DEFAULT 0,
                pvp_count INTEGER DEFAULT 0,
                UNIQUE(user_id, date),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        # To'lov tarixi
        await db.execute('''
            CREATE TABLE IF NOT EXISTS payment_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                plan TEXT NOT NULL,
                amount INTEGER NOT NULL,
                currency TEXT NOT NULL,
                -- STARS | SOM
                telegram_charge_id TEXT,
                status TEXT DEFAULT 'pending',
                -- pending | completed | refunded
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        await db.commit()


# ==================== PREMIUM FUNKSIYALARI ====================

async def get_user_plan(user_id):
    """Foydalanuvchi premium rejimini olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT plan, expires_at FROM premium_users WHERE user_id = ?',
            (user_id,))
        row = await cursor.fetchone()

        if not row:
            return 'free', None

        plan, expires_at = row
        if plan == 'free':
            return 'free', None

        # Muddati tugaganmi?
        if expires_at:
            from datetime import datetime
            now = datetime.now()
            exp = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
            if now > exp:
                # Muddati tugagan — bepulga qaytarish
                await db.execute(
                    "UPDATE premium_users SET plan='free', expires_at=NULL WHERE user_id=?",
                    (user_id,))
                await db.commit()
                return 'free', None

        return plan, expires_at


async def set_user_premium(user_id, plan, given_by='purchase', stars=0, som=0):
    """Premiumni berish"""
    from datetime import datetime, timedelta
    now = datetime.now()
    days = PREMIUM_PLANS[plan]['duration_days']
    expires = (now + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO premium_users (user_id, plan, started_at, expires_at, given_by, stars_paid, som_paid)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                plan=excluded.plan,
                started_at=excluded.started_at,
                expires_at=excluded.expires_at,
                given_by=excluded.given_by,
                stars_paid=excluded.stars_paid,
                som_paid=excluded.som_paid
        ''', (user_id, plan, now_str, expires, given_by, stars, som))
        await db.commit()
    return expires


async def remove_premium(user_id):
    """Premiumni olib qo'yish"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE premium_users SET plan='free', expires_at=NULL WHERE user_id=?",
            (user_id,))
        await db.commit()


async def get_daily_usage(user_id):
    """Bugungi foydalanish sonini olish"""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT quiz_count, pvp_count FROM daily_usage WHERE user_id=? AND date=?',
            (user_id, today))
        row = await cursor.fetchone()
        return row if row else (0, 0)


async def increment_daily_usage(user_id, kind='quiz'):
    """Kunlik foydalanishni oshirish"""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_PATH) as db:
        if kind == 'quiz':
            await db.execute('''
                INSERT INTO daily_usage (user_id, date, quiz_count)
                VALUES (?, ?, 1)
                ON CONFLICT(user_id, date) DO UPDATE SET quiz_count = quiz_count + 1
            ''', (user_id, today))
        else:
            await db.execute('''
                INSERT INTO daily_usage (user_id, date, pvp_count)
                VALUES (?, ?, 1)
                ON CONFLICT(user_id, date) DO UPDATE SET pvp_count = pvp_count + 1
            ''', (user_id, today))
        await db.commit()


async def check_quiz_limit(user_id):
    """Quiz limitni tekshirish. (can_play, is_warning, used, limit)"""
    plan, _ = await get_user_plan(user_id)
    limits = PREMIUM_PLANS[plan]
    quiz_limit = limits['quiz_limit']
    warning = limits.get('quiz_warning', quiz_limit)

    quiz_count, _ = await get_daily_usage(user_id)

    if quiz_count >= quiz_limit:
        return False, False, quiz_count, quiz_limit
    if plan == 'free' and quiz_count >= warning:
        return True, True, quiz_count, quiz_limit   # ogohlantirish
    return True, False, quiz_count, quiz_limit


async def check_pvp_limit(user_id):
    """PvP limitni tekshirish"""
    plan, _ = await get_user_plan(user_id)
    pvp_limit = PREMIUM_PLANS[plan]['pvp_limit']
    _, pvp_count = await get_daily_usage(user_id)
    return pvp_count < pvp_limit, pvp_count, pvp_limit


def get_xp_multiplier_sync(user_id):
    """XP multiplier sinxron olish"""
    plan, _ = asyncio.run(get_user_plan(user_id))
    return PREMIUM_PLANS[plan]['xp_multiplier']


def get_plan_badge(plan):
    """Plan badge belgisi"""
    return PREMIUM_PLANS.get(plan, {}).get('badge', '')


async def get_premium_stats():
    """Admin uchun premium statistika"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT plan, COUNT(*) as cnt
            FROM premium_users
            WHERE plan != 'free'
            GROUP BY plan
        ''')
        by_plan = await cursor.fetchall()

        cursor = await db.execute(
            "SELECT COALESCE(SUM(stars_paid),0), COALESCE(SUM(som_paid),0) FROM premium_users")
        totals = await cursor.fetchone()
        return by_plan, totals


# ==================== PREMIUM MENYU ====================

@bot.message_handler(func=lambda m: m.text == "💎 Premium")
def premium_menu(message):
    """Premium asosiy menyu"""
    user_id = message.from_user.id
    plan, expires_at = asyncio.run(get_user_plan(user_id))
    quiz_used, pvp_used = asyncio.run(get_daily_usage(user_id))
    plan_info = PREMIUM_PLANS[plan]

    if plan == 'free':
        quiz_left = plan_info['quiz_limit'] - quiz_used
        pvp_left = plan_info['pvp_limit'] - pvp_used
        status_text = (
            f"🆓 Siz hozir bepul rejimdasiz\n\n"
            f"📊 Bugungi foydalanish:\n"
            f"  ❓ Savol: {quiz_used}/{plan_info['quiz_limit']} "
            f"({'⚠️' if quiz_used >= 150 else '✅'})\n"
            f"  ⚔️ PvP: {pvp_used}/{plan_info['pvp_limit']} "
            f"({'⚠️' if pvp_used >= 13 else '✅'})\n\n"
            f"💡 Premium olsangiz:\n"
            f"  • Cheksiz savol va PvP\n"
            f"  • 2x — 5x XP mukofot\n"
            f"  • Maxsus badge va unvon\n"
        )
    else:
        badge = plan_info['badge']
        exp_str = expires_at[:10] if expires_at else '—'
        multi = plan_info['xp_multiplier']
        status_text = (
            f"{badge} Siz {plan_info['name']} premiumdasiz!\n\n"
            f"📅 Tugash sanasi: {exp_str}\n"
            f"⚡ XP multiplier: {multi}x\n"
            f"❓ Savollar: Cheksiz\n"
            f"⚔️ PvP: Cheksiz\n\n"
            f"🎁 Imtiyozlaringiz to'liq faol!"
        )

    markup = types.InlineKeyboardMarkup()
    if plan == 'free':
        markup.row(
            types.InlineKeyboardButton("🥈 Silver — 15⭐ / 3,000so'm", callback_data="buy_silver"),
        )
        markup.row(
            types.InlineKeyboardButton("🥇 Gold — 25⭐ / 5,000so'm", callback_data="buy_gold"),
        )
        markup.row(
            types.InlineKeyboardButton("💎 Diamond — 50⭐ / 10,000so'm", callback_data="buy_diamond"),
        )
    else:
        markup.row(
            types.InlineKeyboardButton("🔄 Uzaytirish", callback_data=f"buy_{plan}"),
        )
        markup.row(
            types.InlineKeyboardButton("⬆️ Yangilash", callback_data="premium_upgrade"),
        )
    markup.row(
        types.InlineKeyboardButton("📋 Tariflar batafsil", callback_data="premium_compare"),
    )

    bot.send_message(message.chat.id,
        f"💎 PREMIUM TIZIMI\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"{status_text}",
        reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "premium_compare")
def premium_compare_cb(call):
    """Tariflarni solishtirish"""
    bot.answer_callback_query(call.id)
    text = (
        "📋 TARIFLAR SOLISHTIRMASI\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "           🆓Free  🥈Silver 🥇Gold  💎Diamond\n"
        "Savol/kun:  200    ♾       ♾       ♾\n"
        "PvP/kun:     15    ♾       ♾       ♾\n"
        "XP bonus:    1x    2x      3x      5x\n"
        "Badge:       —     🥈      🥇      💎\n"
        "Turnir:      ✅    ✅      🆓      🆓\n"
        "Maxsus unvon:—     —       —       ✅\n\n"
        "💰 Narx (oylik):\n"
        "🥈 Silver:  15⭐ yoki 3,000 so'm\n"
        "🥇 Gold:    25⭐ yoki 5,000 so'm\n"
        "💎 Diamond: 50⭐ yoki 10,000 so'm\n\n"
        "⭐ Telegram Stars — to'g'ridan-to'g'ri botda!\n"
        "💳 So'm — @admin ga murojaat qiling"
    )
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🥈 Silver olish", callback_data="buy_silver"),
        types.InlineKeyboardButton("🥇 Gold olish", callback_data="buy_gold"),
    )
    markup.row(
        types.InlineKeyboardButton("💎 Diamond olish", callback_data="buy_diamond"),
    )
    bot.send_message(call.message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "premium_upgrade")
def premium_upgrade_cb(call):
    """Premium yangilash"""
    user_id = call.from_user.id
    plan, _ = asyncio.run(get_user_plan(user_id))
    bot.answer_callback_query(call.id)

    markup = types.InlineKeyboardMarkup()
    if plan in ['free', 'silver']:
        markup.add(types.InlineKeyboardButton("🥇 Gold ga o'tish — 25⭐", callback_data="buy_gold"))
    if plan in ['free', 'silver', 'gold']:
        markup.add(types.InlineKeyboardButton("💎 Diamond ga o'tish — 50⭐", callback_data="buy_diamond"))
    bot.send_message(call.message.chat.id,
        "⬆️ Qaysi tarifga o'tmoqchisiz?", reply_markup=markup)


# ==================== TELEGRAM STARS TO'LOV ====================

PLAN_STARS = {'silver': 15, 'gold': 25, 'diamond': 50}
PLAN_TITLES = {
    'silver': '🥈 Silver Premium — 1 oy',
    'gold':   '🥇 Gold Premium — 1 oy',
    'diamond':'💎 Diamond Premium — 1 oy',
}
PLAN_DESCS = {
    'silver': 'Cheksiz savol, 2x XP, 🥈 badge',
    'gold':   'Cheksiz savol, 3x XP, 🥇 badge, bepul turnir',
    'diamond':'Cheksiz savol, 5x XP, 💎 badge, maxsus unvon',
}


@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_") and
                             call.data.split("_")[1] in PLAN_STARS)
def buy_premium_cb(call):
    """Premium sotib olish — Stars invoice yuborish"""
    plan = call.data.split("_")[1]
    stars = PLAN_STARS[plan]
    bot.answer_callback_query(call.id)

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(f"⭐ {stars} Stars bilan to'lash", pay=True)
    )
    markup.row(
        types.InlineKeyboardButton("💳 So'm bilan to'lash (admin)", callback_data=f"pay_som_{plan}")
    )

    bot.send_invoice(
        chat_id=call.message.chat.id,
        title=PLAN_TITLES[plan],
        description=PLAN_DESCS[plan],
        invoice_payload=f"premium_{plan}_{call.from_user.id}",
        provider_token="",           # Stars uchun bo'sh qoldiriladi
        currency="XTR",              # Telegram Stars
        prices=[types.LabeledPrice(label=PLAN_TITLES[plan], amount=stars)],
        reply_markup=markup
    )


@bot.pre_checkout_query_handler(func=lambda q: True)
def pre_checkout(pre_checkout_query):
    """To'lovni tasdiqlash"""
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@bot.message_handler(content_types=['successful_payment'])
def successful_payment(message):
    """Muvaffaqiyatli to'lov"""
    user_id = message.from_user.id
    payload = message.successful_payment.invoice_payload
    stars = message.successful_payment.total_amount
    charge_id = message.successful_payment.telegram_payment_charge_id

    # payload: premium_silver_12345
    parts = payload.split("_")
    if len(parts) >= 2 and parts[0] == "premium":
        plan = parts[1]
        expires = asyncio.run(set_user_premium(user_id, plan, given_by='purchase', stars=stars))

        # To'lovni saqlash
        async def save_payment():
            from datetime import datetime
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute('''
                    INSERT INTO payment_history
                    (user_id, plan, amount, currency, telegram_charge_id, status, created_at)
                    VALUES (?, ?, ?, 'STARS', ?, 'completed', ?)
                ''', (user_id, plan, stars, charge_id,
                      datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                await db.commit()
        asyncio.run(save_payment())

        badge = PREMIUM_PLANS[plan]['badge']
        multi = PREMIUM_PLANS[plan]['xp_multiplier']
        exp_str = expires[:10] if expires else '—'

        bot.send_message(
            message.chat.id,
            f"🎉 TO'LOV MUVAFFAQIYATLI!\n\n"
            f"{badge} {PLAN_TITLES[plan]} faollashtirildi!\n\n"
            f"⭐ To'langan: {stars} Stars\n"
            f"📅 Tugash: {exp_str}\n"
            f"⚡ XP bonus: {multi}x\n\n"
            f"Barcha imtiyozlar hoziroq faol! 🚀"
        )

        # Adminga xabar
        try:
            uname = message.from_user.username or message.from_user.first_name
            bot.send_message(
                ADMIN_ID,
                f"💰 YANGI TO'LOV!\n\n"
                f"👤 @{uname} (ID: {user_id})\n"
                f"📦 Plan: {PLAN_TITLES[plan]}\n"
                f"⭐ {stars} Stars\n"
                f"🆔 {charge_id}"
            )
        except Exception:
            pass


@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_som_"))
def pay_som_cb(call):
    """So'm bilan to'lash — admin ga yo'naltirish"""
    plan = call.data.split("_")[2]
    price = PREMIUM_PLANS[plan]['price_som']
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        f"💳 SO'M BILAN TO'LOV\n\n"
        f"📦 Tarif: {PLAN_TITLES[plan]}\n"
        f"💰 Narx: {price:,} so'm\n\n"
        f"To'lov qilish uchun adminga murojaat qiling:\n"
        f"👉 @admin\n\n"
        f"Xabar matni:\n"
        f"\"Premium {plan} olmoqchiman, ID: {call.from_user.id}\""
    )


# ==================== KLAN YARATISH TALABLARI ====================

async def check_clan_create_eligibility(user_id):
    """Klan yaratish uchun level va XP tekshirish"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT level, xp FROM users WHERE user_id = ?', (user_id,))
        row = await cursor.fetchone()
        if not row:
            return False, "Foydalanuvchi topilmadi"

        level, xp = row
        req = CLAN_CREATE_REQUIREMENTS
        if level < req['min_level']:
            return False, (
                f"❌ Klan yaratish uchun kamida {req['min_level']}-daraja kerak!\n"
                f"Sizning darajangiz: {level}\n"
                f"Hali {req['min_level'] - level} daraja oshirish kerak 📈"
            )
        if xp < req['xp_cost']:
            return False, (
                f"❌ Klan yaratish uchun {req['xp_cost']:,} XP kerak!\n"
                f"Sizda: {xp:,} XP\n"
                f"Yana {req['xp_cost'] - xp:,} XP yig'ing 💪"
            )
        return True, "OK"


async def deduct_clan_xp(user_id):
    """Klan yaratganda XP ayirish"""
    cost = CLAN_CREATE_REQUIREMENTS['xp_cost']
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'UPDATE users SET xp = xp - ? WHERE user_id = ?', (cost, user_id))
        await db.commit()


# ==================== QUIZ LIMITNI TEKSHIRUVCHI WRAPPER ====================

def check_and_start_quiz(message):
    """Quiz boshlashdan oldin limit tekshirish"""
    user_id = message.from_user.id

    can_play, is_warning, used, limit = asyncio.run(check_quiz_limit(user_id))
    plan, _ = asyncio.run(get_user_plan(user_id))

    if not can_play:
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("💎 Premium olish", callback_data="premium_compare"))
        bot.send_message(
            message.chat.id,
            f"❌ KUNLIK LIMIT TUGADI!\n\n"
            f"Siz bugun {used} ta savol yechdingiz.\n"
            f"Bepul tarif limiti: {limit} ta/kun\n\n"
            f"💎 Premium oling va cheksiz yozing!\n"
            f"🥈 Silver: 15⭐ yoki 3,000 so'm/oy",
            reply_markup=markup
        )
        return False

    if is_warning:
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("💎 Premium olish", callback_data="buy_silver"))
        bot.send_message(
            message.chat.id,
            f"⚠️ DIQQAT! Bugun {used}/{limit} ta savol yechdingiz.\n"
            f"Yana {limit - used} ta savol qoldi.\n\n"
            f"💡 Cheksiz savol uchun Premium oling!",
            reply_markup=markup
        )

    asyncio.run(increment_daily_usage(user_id, 'quiz'))
    return True


def check_and_start_pvp(message):
    """PvP boshlashdan oldin limit tekshirish"""
    user_id = message.from_user.id
    can_play, used, limit = asyncio.run(check_pvp_limit(user_id))

    if not can_play:
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("💎 Premium olish", callback_data="premium_compare"))
        bot.send_message(
            message.chat.id,
            f"❌ KUNLIK PvP LIMIT TUGADI!\n\n"
            f"Bugun {used}/{limit} ta PvP o'yndingiz.\n\n"
            f"💎 Premium oling — cheksiz PvP!\n"
            f"🥈 Silver: 15⭐ yoki 3,000 so'm/oy",
            reply_markup=markup
        )
        return False

    asyncio.run(increment_daily_usage(user_id, 'pvp'))
    return True


# ==================== ADMIN PREMIUM BOSHQARUVI ====================

@bot.message_handler(func=lambda m: m.text == "💎 Premium Boshqaruvi" and m.from_user.id == ADMIN_ID)
def admin_premium_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("➕ Premium Berish", "➖ Premium Olish")
    markup.row("📊 Premium Statistika", "📋 Premium Foydalanuvchilar")
    markup.row("🔙 Admin Panelga")
    bot.send_message(message.chat.id, "💎 PREMIUM BOSHQARUVI\n\nKerakli bo'lim:", reply_markup=markup)


admin_premium_sessions = {}

@bot.message_handler(func=lambda m: m.text == "➕ Premium Berish" and m.from_user.id == ADMIN_ID)
def admin_give_premium_start(message):
    admin_premium_sessions[message.from_user.id] = {'step': 1}
    bot.send_message(message.chat.id,
        "➕ PREMIUM BERISH\n\n"
        "Foydalanuvchi ID sini kiriting:")


@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and
                     m.from_user.id in admin_premium_sessions and
                     admin_premium_sessions[m.from_user.id].get('step') == 1)
def admin_give_premium_id(message):
    if message.text in ["🔙 Admin Panelga", "💎 Premium Boshqaruvi"]:
        del admin_premium_sessions[message.from_user.id]
        return
    try:
        target_id = int(message.text)
        admin_premium_sessions[message.from_user.id] = {'step': 2, 'target_id': target_id}
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("🥈 Silver", callback_data=f"agive_silver_{target_id}"),
            types.InlineKeyboardButton("🥇 Gold",   callback_data=f"agive_gold_{target_id}"),
        )
        markup.add(types.InlineKeyboardButton("💎 Diamond", callback_data=f"agive_diamond_{target_id}"))
        bot.send_message(message.chat.id,
            f"ID: {target_id}\nQaysi plan berish?", reply_markup=markup)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Faqat raqam kiriting!")


@bot.callback_query_handler(func=lambda call: call.data.startswith("agive_"))
def admin_give_premium_plan(call):
    parts = call.data.split("_")
    plan = parts[1]
    target_id = int(parts[2])
    admin_id = call.from_user.id

    if admin_id in admin_premium_sessions:
        del admin_premium_sessions[admin_id]

    expires = asyncio.run(set_user_premium(target_id, plan, given_by='admin'))
    bot.answer_callback_query(call.id, f"✅ {plan} berildi!")
    badge = PREMIUM_PLANS[plan]['badge']
    bot.send_message(call.message.chat.id,
        f"✅ PREMIUM BERILDI!\n\n"
        f"👤 ID: {target_id}\n"
        f"{badge} Plan: {plan}\n"
        f"📅 Tugash: {expires[:10]}")

    try:
        bot.send_message(target_id,
            f"🎁 SIZGA PREMIUM BERILDI!\n\n"
            f"{badge} {PLAN_TITLES[plan]} faollashtirildi!\n"
            f"📅 Tugash: {expires[:10]}\n\n"
            f"Admin tomonidan sovg'a! 🎉")
    except Exception:
        pass


@bot.message_handler(func=lambda m: m.text == "➖ Premium Olish" and m.from_user.id == ADMIN_ID)
def admin_remove_premium_start(message):
    admin_premium_sessions[message.from_user.id] = {'step': 'remove'}
    bot.send_message(message.chat.id,
        "➖ PREMIUMNI OLIB QO'YISH\n\nFoydalanuvchi ID sini kiriting:")


@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and
                     m.from_user.id in admin_premium_sessions and
                     admin_premium_sessions[m.from_user.id].get('step') == 'remove')
def admin_remove_premium_do(message):
    if message.text in ["🔙 Admin Panelga", "💎 Premium Boshqaruvi"]:
        del admin_premium_sessions[message.from_user.id]
        return
    try:
        target_id = int(message.text)
        asyncio.run(remove_premium(target_id))
        del admin_premium_sessions[message.from_user.id]
        bot.send_message(message.chat.id, f"✅ ID {target_id} premiumdan chiqarildi!")
        try:
            bot.send_message(target_id, "ℹ️ Sizning premium obunangiz bekor qilindi.")
        except Exception:
            pass
    except ValueError:
        bot.send_message(message.chat.id, "❌ Faqat raqam kiriting!")


@bot.message_handler(func=lambda m: m.text == "📊 Premium Statistika" and m.from_user.id == ADMIN_ID)
def admin_premium_stats(message):
    by_plan, totals = asyncio.run(get_premium_stats())
    stars_total, som_total = totals
    text = (
        "📊 PREMIUM STATISTIKA\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
    )
    for plan, cnt in by_plan:
        badge = PREMIUM_PLANS.get(plan, {}).get('badge', '')
        text += f"{badge} {plan.capitalize()}: {cnt} ta\n"
    text += (
        f"\n💰 Jami daromad:\n"
        f"⭐ Stars: {stars_total}\n"
        f"💳 So'm: {som_total:,} so'm\n"
    )
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: m.text == "📋 Premium Foydalanuvchilar" and m.from_user.id == ADMIN_ID)
def admin_premium_list(message):
    async def get_list():
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute('''
                SELECT pu.user_id, u.username, pu.plan, pu.expires_at, pu.given_by
                FROM premium_users pu
                LEFT JOIN users u ON pu.user_id = u.user_id
                WHERE pu.plan != 'free'
                ORDER BY pu.plan DESC
            ''')
            return await cursor.fetchall()

    rows = asyncio.run(get_list())
    if not rows:
        bot.send_message(message.chat.id, "😴 Hali premium foydalanuvchilar yo'q!")
        return

    text = "📋 PREMIUM FOYDALANUVCHILAR\n━━━━━━━━━━━━━━━━━━━\n\n"
    for (uid, uname, plan, expires, given_by) in rows:
        badge = PREMIUM_PLANS.get(plan, {}).get('badge', '')
        exp = expires[:10] if expires else '—'
        text += (
            f"{badge} @{uname or uid} (ID:{uid})\n"
            f"   Plan: {plan} | Tugash: {exp} | {given_by}\n"
        )
    bot.send_message(message.chat.id, text)



# ==================== MAIN ====================
def main():
    print("🤖 Bot ishga tushmoqda...")
    asyncio.run(init_db())
    asyncio.run(init_referral_table())
    asyncio.run(init_season_table()) 
    asyncio.run(init_learning_table()) 
    asyncio.run(init_levels_table())
    asyncio.run(init_pvp_table())
    asyncio.run(init_speed_quiz_table()) 
    asyncio.run(init_clan_tables())
    asyncio.run(init_achievements_table())
    asyncio.run(init_group_quiz_table())
    asyncio.run(init_reminder_table())
    asyncio.run(init_tournament_tables())
    asyncio.run(init_premium_tables())

    print("✅ Ma'lumotlar bazasi tayyor!")
    print("🚀 Bot ishlayapti!")
    bot.infinity_polling()


if __name__ == '__main__':
    main()

