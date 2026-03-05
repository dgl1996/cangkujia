from database import engine, Base
import models

# 创建所有表
Base.metadata.create_all(bind=engine)
print("数据库表创建成功")