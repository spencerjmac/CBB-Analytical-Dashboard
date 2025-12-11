"""
SQLite database operations for KenPom data storage.
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional


class KenPomDB:
    """Database handler for KenPom data."""
    
    def __init__(self, db_path: str = "kenpom_data.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self.conn = None
        self._create_tables()
    
    def _get_connection(self):
        """Get or create database connection."""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Teams table - stores team information
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_name TEXT NOT NULL,
                conference TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(team_name)
            )
        """)
        
        # Rankings table - stores daily rankings and metrics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rankings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER NOT NULL,
                date DATE NOT NULL,
                rank INTEGER,
                adj_em REAL,
                adj_o REAL,
                adj_d REAL,
                adj_tempo REAL,
                luck REAL,
                sos_adj_em REAL,
                opp_o REAL,
                opp_d REAL,
                ncsos_adj_em REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_id) REFERENCES teams(id),
                UNIQUE(team_id, date)
            )
        """)
        
        # Games table - stores game predictions/results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                team_id INTEGER NOT NULL,
                opponent_id INTEGER,
                opponent_name TEXT,
                location TEXT,
                predicted_score REAL,
                actual_score INTEGER,
                win_probability REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_id) REFERENCES teams(id),
                FOREIGN KEY (opponent_id) REFERENCES teams(id)
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rankings_date ON rankings(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rankings_team_date ON rankings(team_id, date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_games_date ON games(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_games_team ON games(team_id)")
        
        conn.commit()
    
    def insert_team(self, team_name: str, conference: Optional[str] = None) -> int:
        """Insert or get team ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR IGNORE INTO teams (team_name, conference)
            VALUES (?, ?)
        """, (team_name, conference))
        
        cursor.execute("SELECT id FROM teams WHERE team_name = ?", (team_name,))
        result = cursor.fetchone()
        conn.commit()
        
        return result['id'] if result else None
    
    def insert_ranking(self, team_id: int, date: str, ranking_data: Dict):
        """Insert ranking data for a team on a specific date."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO rankings (
                team_id, date, rank, adj_em, adj_o, adj_d, adj_tempo,
                luck, sos_adj_em, opp_o, opp_d, ncsos_adj_em
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            team_id,
            date,
            ranking_data.get('rank'),
            ranking_data.get('adj_em'),
            ranking_data.get('adj_o'),
            ranking_data.get('adj_d'),
            ranking_data.get('adj_tempo'),
            ranking_data.get('luck'),
            ranking_data.get('sos_adj_em'),
            ranking_data.get('opp_o'),
            ranking_data.get('opp_d'),
            ranking_data.get('ncsos_adj_em')
        ))
        
        conn.commit()
    
    def insert_game(self, date: str, team_id: int, opponent_name: str,
                   opponent_id: Optional[int] = None, location: Optional[str] = None,
                   predicted_score: Optional[float] = None, actual_score: Optional[int] = None,
                   win_probability: Optional[float] = None):
        """Insert game data."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO games (
                date, team_id, opponent_id, opponent_name, location,
                predicted_score, actual_score, win_probability
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (date, team_id, opponent_id, opponent_name, location,
              predicted_score, actual_score, win_probability))
        
        conn.commit()
    
    def get_latest_rankings(self, limit: int = 50) -> List[Dict]:
        """Get latest rankings for all teams."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        latest_date = cursor.execute("SELECT MAX(date) FROM rankings").fetchone()[0]
        
        cursor.execute("""
            SELECT t.team_name, t.conference, r.rank, r.adj_em, r.adj_o, r.adj_d,
                   r.adj_tempo, r.luck, r.date
            FROM rankings r
            JOIN teams t ON r.team_id = t.id
            WHERE r.date = ?
            ORDER BY r.rank
            LIMIT ?
        """, (latest_date, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None



