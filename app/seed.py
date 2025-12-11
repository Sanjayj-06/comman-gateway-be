from sqlalchemy.orm import Session
from app.db.models import User, Rule, UserRole, RuleAction
from app.utils import generate_api_key


def seed_database(db: Session):
    """
    Seed the database with initial data:
    - Default admin user
    - Default rules for common dangerous and safe commands
    """
    
    
    admin = db.query(User).filter(User.username == "admin").first()
    if admin:
        print("✓ Admin user already exists")
        print(f"  Username: admin")
        print(f"  API Key: {admin.api_key}")
    else:
        
        admin_api_key = generate_api_key()
        admin = User(
            username="admin",
            api_key=admin_api_key,
            role=UserRole.ADMIN,
            credits=1000
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("✓ Created default admin user")
        print(f"  Username: admin")
        print(f"  API Key: {admin_api_key}")
        print(f"  Credits: 1000")
    
    
    existing_rules = db.query(Rule).count()
    if existing_rules > 0:
        print(f"✓ {existing_rules} rules already exist")
    else:
        
        default_rules = [
            {
                "pattern": r":\(\)\{ :\|:& \};:",
                "action": RuleAction.AUTO_REJECT,
                "description": "Fork bomb - dangerous recursive process",
                "priority": 0
            },
            {
                "pattern": r"rm\s+-rf\s+/",
                "action": RuleAction.AUTO_REJECT,
                "description": "Delete root directory - extremely dangerous",
                "priority": 0
            },
            {
                "pattern": r"mkfs\.",
                "action": RuleAction.AUTO_REJECT,
                "description": "Format filesystem - data loss",
                "priority": 0
            },
            {
                "pattern": r"dd\s+if=/dev/(zero|random)\s+of=/dev/",
                "action": RuleAction.AUTO_REJECT,
                "description": "Overwrite disk - data loss",
                "priority": 0
            },
            {
                "pattern": r"chmod\s+-R\s+777\s+/",
                "action": RuleAction.AUTO_REJECT,
                "description": "Make all files world-writable - security risk",
                "priority": 0
            },
            {
                "pattern": r"git\s+(status|log|diff|branch|show)",
                "action": RuleAction.AUTO_ACCEPT,
                "description": "Safe git read operations",
                "priority": 1
            },
            {
                "pattern": r"^(ls|cat|pwd|echo|which|whoami|date|uptime)",
                "action": RuleAction.AUTO_ACCEPT,
                "description": "Safe basic commands",
                "priority": 1
            },
            {
                "pattern": r"^grep\s+",
                "action": RuleAction.AUTO_ACCEPT,
                "description": "Text search - safe",
                "priority": 1
            },
            {
                "pattern": r"^find\s+",
                "action": RuleAction.AUTO_ACCEPT,
                "description": "File search - safe",
                "priority": 1
            }
        ]
        
        for rule_data in default_rules:
            rule = Rule(**rule_data, created_by=admin.id)
            db.add(rule)
        
        db.commit()
        print(f"✓ Created {len(default_rules)} default rules")
    
    print("\n" + "="*50)
    print("DATABASE SEEDED SUCCESSFULLY")
    print("="*50)


if __name__ == "__main__":
    from app.db.session import SessionLocal
    from app.db.base import Base
    from app.db.session import engine
    
    
    Base.metadata.create_all(bind=engine)
    
    
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
