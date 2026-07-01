from model import Session, RequestLog

session = Session()
log = RequestLog(
    user_id="vansh",
    model="gpt-4",
    tokens_in=150,
    tokens_out=300,
    cost=0.0195,
    cached=False
)

session.add(log)
session.commit()

logs = session.query(RequestLog).all()
for l in logs:
    print(l)

session.close()
