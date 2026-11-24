import sys
from sqlalchemy import create_engine, inspect, text
from database.connection import DATABASE_URL

engine = create_engine(DATABASE_URL)
inspector = inspect(engine)
table_name = 'career_readiness_reports'

print(f'\n--- Table: {table_name} ---')
if table_name in inspector.get_table_names():
    print('Table exists: YES')
    columns = inspector.get_columns(table_name)
    print('\nColumns:')
    for col in columns:
        print(f"  - {col['name']} ({col['type']}): nullable={col['nullable']}, default={col.get('default')}")
    
    fks = inspector.get_foreign_keys(table_name)
    print('\nForeign Keys:')
    for fk in fks:
        referred = fk['referred_table']
        cols = fk['constrained_columns']
        ref_cols = fk['referred_columns']
        options = fk['options']
        ondelete = options.get('ondelete')
        print(f"  - {cols[0]} -> {referred}.{ref_cols[0]} ON DELETE {ondelete}")
else:
    print('Table exists: NO')

print('\n--- Verifying Existing Data ---')
with engine.connect() as conn:
    print('Questions:', conn.scalar(text('SELECT COUNT(*) FROM interview_questions')))
    print('Users:', conn.scalar(text('SELECT COUNT(*) FROM users')))
    print('Resumes:', conn.scalar(text('SELECT COUNT(*) FROM resumes')))
    print('Sessions:', conn.scalar(text('SELECT COUNT(*) FROM interview_sessions')))
    print('Responses:', conn.scalar(text('SELECT COUNT(*) FROM interview_responses')))
