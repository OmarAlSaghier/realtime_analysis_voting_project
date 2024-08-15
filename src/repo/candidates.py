
def check_candidates(cur):
    cur.execute("""
        SELECT row_to_json(t)
        FROM (
            SELECT * FROM candidates
        ) t;
    """)
    candidates = cur.fetchall()
    candidates = [candidate[0] for candidate in candidates]
    if len(candidates) == 0:
        raise Exception("No candidates found in database")
    else:
        print(candidates)
    
    return candidates
