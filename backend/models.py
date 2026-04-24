from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    phone = Column(String, nullable=True)
    nickname = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String, unique=True, index=True, nullable=False)  # 订单号
    user_id = Column(Integer, index=True, nullable=False)  # 用户ID
    amount = Column(Float, nullable=False)  # 订单金额（元）
    paid_amount = Column(Float, default=0)  # 实际支付金额（元）
    status = Column(String, default="pending")  # pending, paid, failed, cancelled
    product_name = Column(String, nullable=True)  # 产品名称
    description = Column(Text, nullable=True)  # 订单描述
    transaction_id = Column(String, nullable=True)  # 微信支付订单号
    fail_reason = Column(Text, nullable=True)  # 失败原因
    paid_at = Column(DateTime(timezone=True), nullable=True)  # 支付时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class UserLicense(Base):
    __tablename__ = "user_licenses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    license_type = Column(String, nullable=False)  # basic, pro, enterprise
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Integer, default=1)  # 1=有效, 0=无效
    order_no = Column(String, nullable=True)  # 关联的订单号
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)  # 用户ID
    plan_type = Column(String, nullable=False)  # monthly, quarterly, halfyear, yearly
    status = Column(String, default="active")  # active, expired, cancelled
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    expire_at = Column(DateTime(timezone=True), nullable=False)
    order_no = Column(String, nullable=True)  # 关联的订单号
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Layout(Base):
    __tablename__ = "layouts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    user_id = Column(Integer, index=True)
    data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Model(Base):
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String, index=True)
    path = Column(String)
    params = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())