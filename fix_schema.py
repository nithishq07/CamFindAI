import re

with open("app/models/schema.py", "r") as f:
    content = f.read()

content = content.replace("from datetime import datetime", "from datetime import datetime, timezone")
content = content.replace("Column(DateTime, nullable=True)", "Column(DateTime(timezone=True), nullable=True)")
content = content.replace("Column(DateTime, default=datetime.utcnow)", "Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))")

with open("app/models/schema.py", "w") as f:
    f.write(content)

