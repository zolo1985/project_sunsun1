
from flask_login import AnonymousUserMixin, UserMixin
from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, PickleType,
                        Table, Text, Unicode)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableList

from webapp import bcrypt, jwt
from webapp.database import Base
from webapp.utils import generate_uuid

from . import cache


roles_table = Table('role_users', Base.metadata,
    Column('user_id', ForeignKey('user.id')),
    Column('role_id', ForeignKey('role.id')))


class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    public_id = Column(Unicode(50), nullable=False, unique=True, default=generate_uuid)

    name                                = Column(Unicode(255))
    description                         = Column(Unicode(255), default='user')

    users = relationship("User",
            secondary=roles_table,
            back_populates="roles")
    

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '{}'.format(self.name)



class User(Base, UserMixin):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    public_id = Column(Unicode(50), nullable=False, unique=True, default=generate_uuid)

    company_name                                 = Column(Unicode(255), nullable=False)
    firstname                                    = Column(Unicode(255), nullable=False)
    lastname                                     = Column(Unicode(255), nullable=False)
    password                                     = Column(Text)
    email                                        = Column(Unicode(255), unique=True)
    phone                                        = Column(Unicode(255), unique=True)
    status                                       = Column(Unicode(100))
    is_authorized                                = Column(Boolean, default=True)
    is_invoiced                                  = Column(Boolean, default=False)
    refresh_token                                = Column(Unicode(2000))
    current_orders_list                          = Column(MutableList.as_mutable(PickleType), default=[])
    avatar_id                                    = Column(Unicode(255))
    fee                                          = Column(Integer, nullable=False, default = 3000)
    created_date                                 = Column(DateTime)
    modified_date                                = Column(DateTime)
    last_login_date                              = Column(DateTime)

    roles = relationship("Role", secondary=roles_table)
    products = relationship("Product", back_populates="supplier")
    pickups = relationship("PickupTask", back_populates="supplier")
    dropoffs = relationship("DropoffTask", back_populates="supplier")
    deliveries = relationship("Delivery", back_populates="user")
    returns = relationship("DriverReturn", back_populates="driver")
    substractions = relationship("DriverProductReturn", back_populates="driver")
    total_inventories = relationship("TotalInventory", back_populates="supplier")
    payment_histories = relationship("AccountantPaymentHistory", back_populates="accountant")

    def __repr__(self):
        return self.firstname

    @property
    def is_authenticated(self):
        if isinstance(self, AnonymousUserMixin):
            return False
        else:
            return True
    
    @property
    def is_active(self):
        return True

    
    @property
    def is_anonymous(self):
        if isinstance(self, AnonymousUserMixin):
            return True
        else:
            return False

    def get_id(self):
        return str(self.id)

    @cache.memoize(60)
    def has_role(self, name):
        for role in self.roles:
            if role.name == name:
                return True
        return False

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    # Register a callback function that takes whatever object is passed in as the
    # identity when creating JWTs and converts it to a JSON serializable format.
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.id

    # Register a callback function that loads a user from your database whenever
    # a protected route is accessed. This should return any python object on a
    # successful lookup, or None if the lookup failed for any reason (for example
    # if the user has been deleted from the database).
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity).one_or_none()


product_color_table = Table('product_colors', Base.metadata,
    Column('product_color_id', ForeignKey('product_color.id')),
    Column('product_id', ForeignKey('product.id')))


class ProductColor(Base):
    __tablename__ = 'product_color'

    id = Column(Integer, primary_key=True)
    public_id = Column(Unicode(50), nullable=False, unique=True, default=generate_uuid)

    name                                    = Column(Unicode(50), nullable=False, unique=True)

    products = relationship("Product",
                            secondary=product_color_table,
                            back_populates="colors")
    
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '{}'.format(self.name)


product_size_table = Table('product_sizes', Base.metadata,
    Column('product_size_id', ForeignKey('product_size.id')),
    Column('product_id', ForeignKey('product.id')))


class ProductSize(Base):
    __tablename__ = 'product_size'

    id = Column(Integer, primary_key=True)
    public_id = Column(Unicode(50), nullable=False, unique=True, default=generate_uuid)

    name                                    = Column(Unicode(50), nullable=False, unique=True)

    products = relationship("Product",
                            secondary=product_size_table,
                            back_populates="sizes")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '{}'.format(self.name)


class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True)
    public_id = Column(Unicode(50), nullable=False, unique=True, default=generate_uuid)

    name                                    = Column(Unicode(255), nullable=False)
    price                                   = Column(Integer, nullable=False, default = 0)
    description                             = Column(Text)
    usage_guide                             = Column(Text)
    image                                   = Column(Unicode(255))
    created_date                            = Column(DateTime)
    modified_date                           = Column(DateTime)
    is_active                               = Column(Boolean, default=True)
    supplier_id                             = Column(Integer, ForeignKey('user.id'))

    supplier = relationship("User", back_populates="products")

    colors = relationship("ProductColor", secondary=product_color_table)

    sizes = relationship("ProductSize", secondary=product_size_table)

    inventory = relationship("Inventory", back_populates="product")

    product_pickups = relationship("PickupTaskDetail", back_populates="product")

    product_substracts = relationship("DriverProductReturn", back_populates="product")

    product_dropoffs = relationship("DropoffTaskDetail", back_populates="product")

    total_inventories_product = relationship("TotalInventory", back_populates="total_inventory_product")


    def __repr__(self):
        return '{}'.format(self.name)


class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    public_id = Column(Unicode(50), nullable=False, unique=True, default=generate_uuid)

    phone                                    = Column(Text)
    phone_more                               = Column(Text)
    district                                 = Column(Unicode(255))
    khoroo                                   = Column(Unicode(255))
    city                                     = Column(Unicode(255))
    aimag                                    = Column(Unicode(255))
    address                                  = Column(Text)
    created_date                             = Column(DateTime)
    modified_date                            = Column(DateTime)
    delivery_id                              = Column(Integer, ForeignKey("delivery.id"))

    delivery = relationship("Delivery", back_populates="addresses")

    def __repr__(self):
        return f'%s %s, %s, %s, %s'%(self.aimag if self.aimag is not None else "", self.district, self.khoroo, self.address, self.phone)

regions_table = Table('region_orders', Base.metadata,
    Column('delivery_id', ForeignKey('delivery.id', ondelete="CASCADE")),
    Column('region_id', ForeignKey('region.id', ondelete="CASCADE")))


class Region(Base):
    __tablename__ = 'region'

    id = Column(Integer, primary_key=True)
    public_id = Column(Unicode(50), nullable=False, unique=True, default=generate_uuid)

    name                                = Column(Unicode(255))
    description                         = Column(Unicode(255), default='describes region')    

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '{}'.format(self.name)


delivery_payment_types_table = Table('delivery_payment_types', Base.metadata,
    Column('delivery_id', ForeignKey('delivery.id', ondelete="SET NULL")),
    Column('payment_type_id', ForeignKey('payment_type.id', ondelete="SET NULL")))


class PaymentType(Base):
    __tablename__ = 'payment_type'

    id = Column(Integer, primary_key=True)
    public_id = Column(Unicode(50), nullable=False, unique=True, default=generate_uuid)

    name                                = Column(Unicode(255))
    amount                              = Column(Integer)
    description                         = Column(Unicode(255), default='payment type description')

    deliveries = relationship("Delivery", secondary=delivery_payment_types_table, back_populates="payment_types")

    def __init__(self, name, amount):
        self.name = name
        self.amount = amount

    def __repr__(self):
        return '{}'.format(self.name)


class District(Base):
    __tablename__ = 'district'

    id = Column(Integer, primary_key=True)
    public_id = Column(Unicode(50), nullable=False, unique=True, default=generate_uuid)

    name                                = Column(Unicode(255))
    description                         = Column(Unicode(255), default='district information')
    

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '{}'.format(self.name)



class Aimag(Base):
    __tablename__ = 'aimag'

    id = Column(Integer, primary_key=True)
    public_id = Column(Unicode(50), nullable=False, unique=True, default=generate_uuid)

    name                                = Column(Unicode(255))
    group                               = Column(Integer)
    description                         = Column(Unicode(255), default='aimag information')
    

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '{}'.format(self.name)



class DeliveryDetail(Base):
    __tablename__ = 'delivery_detail'

    id = Column(Integer, primary_key=True)
    public_id = Column(Unicode(50), nullable=False, unique=True, default=generate_uuid)

    quantity                                 = Column(Integer, nullable=False, default=0)
    created_date                             = Column(DateTime)
    modified_date                            = Column(DateTime)

    phone                                    = Column(Unicode(255))
    phone_more                               = Column(Unicode(255))
    district                                 = Column(Unicode(255))
    khoroo                                   = Column(Unicode(255))
    aimag                                    = Column(Unicode(255))
    address                                  = Column(Unicode(255))

    delivery_id                              = Column(Integer, ForeignKey('delivery.id'))
    product_id                               = Column(Integer, ForeignKey('product.id'))

    products = relationship("Product")

    def __repr__(self):
        return f'(Тоо ширхэг: %s, Барааны нэр: %s)'%(self.quantity, self.products if self.products is not None else "")
        

class PaymentDetail(Base):
    __tablename__ = 'payment_detail'

    id = Column(Integer, primary_key=True)
    public_id = Column(Unicode(50), nullable=False, unique=True, default=generate_uuid)

    card_amount                              = Column(Integer, nullable=False, default=0)
    cash_amount                              = Column(Integer, nullable=False, default=0)
    created_date                             = Column(DateTime)
    modified_date                            = Column(DateTime)
    delivery_id                              = Column(Integer, ForeignKey('delivery.id'))

    delivery = relationship("Delivery", back_populates="payment_details")

    def __repr__(self):
        return f'Дансаар: %s₮, Бэлнээр: %s₮'%(self.card_amount, self.cash_amount)


class Delivery(Base):
    __tablename__ = 'delivery'

    id = Column(Integer, primary_key=True)
    public_id = Column(Unicode(50), nullable=False, unique=True, default=generate_uuid)

    supplier_company_name                    = Column(Unicode(255))
    status                                   = Column(Unicode(255))
    delivery_attempts                        = Column(Integer)
    total_amount                             = Column(Integer, nullable=False, default=0)
    order_type                               = Column(Unicode(50))
    destination_type                         = Column(Unicode(255))
    is_ready                                 = Column(Boolean, default=False)
    is_delivered                             = Column(Boolean, default=False)
    is_postphoned                            = Column(Boolean, default=False)
    is_cancelled                             = Column(Boolean, default=False)
    is_received_from_clerk                   = Column(Boolean, default=False)
    is_driver_received                       = Column(Boolean, default=False)
    is_processed_by_accountant               = Column(Boolean, default=False)
    is_returned                              = Column(Boolean, default=False)

    assigned_driver_id                       = Column(Integer)
    assigned_driver_name                     = Column(Unicode(255))
    assigned_manager_id                      = Column(Unicode(255))

    postphoned_driver_name                   = Column(Unicode(255))

    received_from_clerk_name                 = Column(Unicode(255))
    received_from_clerk_id                   = Column(Integer)
    received_from_clerk_date                 = Column(DateTime)

    processed_accountant_id                  = Column(Integer)
    delivery_region                          = Column(Unicode(255))
    driver_comment                           = Column(Text)
    show_comment                             = Column(Boolean, default=False)
    delivery_date                            = Column(DateTime)
    postphoned_date                          = Column(DateTime)
    created_date                             = Column(DateTime)
    modified_date                            = Column(DateTime)
    delivered_date                           = Column(DateTime)
    user_id                                  = Column(Integer, ForeignKey("user.id"))

    addresses = relationship("Address", back_populates="delivery", uselist=False)
    payment_types = relationship("PaymentType", secondary=delivery_payment_types_table)
    user = relationship("User", back_populates="deliveries")
    delivery_details = relationship("DeliveryDetail", cascade="all, delete", passive_deletes=True)
    payment_details = relationship("PaymentDetail", back_populates="delivery", uselist=False)
    delivery_regions = relationship("Region", secondary=regions_table, passive_deletes=True)
    delivery_returns = relationship("DriverReturn", back_populates="delivery")
    delivery_substacts = relationship("DriverProductReturn", back_populates="delivery")
    delivery_histories = relationship("DriverOrderHistory", back_populates="delivery")

    def __repr__(self):
        return f'Харилцагч: %s'%(self.supplier_company_name)


class Inventory(Base):
    __tablename__ = 'inventory'

    id = Column(Integer, primary_key=True)
    public_id = Column(Unicode(50), nullable=False, unique=True, default=generate_uuid)

    quantity                                = Column(Integer, nullable=False, default = 0)
    status                                  = Column(Boolean, default=False)
    inventory_type                          = Column(Unicode(50))
    is_received_from_driver                 = Column(Boolean, default=False)
    is_returned_to_supplier                 = Column(Boolean, default=False)

    driver_name                             = Column(Unicode(255))
    clerk_name                              = Column(Unicode(255))

    received_date                           = Column(DateTime)
    modified_date                           = Column(DateTime)
    clerk_accepted_date                     = Column(DateTime)
    returned_date                           = Column(DateTime)

    driver_id                               = Column(Integer, ForeignKey('user.id'))
    clerk_id                                = Column(Integer, ForeignKey('user.id'))

    product_id                              = Column(Integer, ForeignKey('product.id'))
    total_inventory_id                      = Column(Integer, ForeignKey("total_inventory.id"))

    product = relationship("Product", back_populates="inventory")
    total_inventory = relationship("TotalInventory", back_populates="total_inventories")
    

class TotalInventory(Base):
    __tablename__ = 'total_inventory'

    id = Column(Integer, primary_key=True)
    public_id = Column(Unicode(50), nullable=False, unique=True, default=generate_uuid)

    quantity                                = Column(Integer, nullable=False, default = 0)
    postphoned_quantity                     = Column(Integer, nullable=False, default = 0)
    cancelled_quantity                      = Column(Integer, nullable=False, default = 0)
    substracted_quantity                    = Column(Integer, nullable=False, default = 0)
    created_date                            = Column(DateTime)
    modified_date                           = Column(DateTime)
    user_id                                 = Column(Integer, ForeignKey('user.id'))
    product_id                              = Column(Integer, ForeignKey('product.id'))

    total_inventory_product = relationship("Product", back_populates="total_inventories_product")
    total_inventories = relationship("Inventory", back_populates="total_inventory")
    supplier = relationship("User", back_populates="total_inventories")



class DriverOrderHistory(Base):
    __tablename__ = 'driver_order_history'

    id = Column(Integer, primary_key=True)
    public_id = Column(Unicode(50), nullable=False, unique=True, default=generate_uuid)

    delivery_status                 = Column(Unicode(50))
    delivery_date                   = Column(DateTime)
    payment_type                    = Column(Unicode(50))
    address                         = Column(Text)
    type                            = Column(Unicode(50))
    supplier_name                   = Column(Unicode(255))

    task_id                         = Column(Integer, ForeignKey('pickup_task.id'))
    dropoff_id                      = Column(Integer, ForeignKey('dropoff_task.id'))
    driver_id                       = Column(Integer, ForeignKey('user.id'))
    delivery_id                     = Column(Integer, ForeignKey('delivery.id'))

    delivery = relationship("Delivery", back_populates="delivery_histories")


class PickupTask(Base):
    __tablename__ = 'pickup_task'

    id = Column(Integer, primary_key=True)
    public_id = Column(Unicode(50), nullable=False, unique=True, default=generate_uuid)

    is_ready                                = Column(Boolean, default=False)
    is_completed                            = Column(Boolean, default=False)
    is_received                             = Column(Boolean, default=False)
    supplier_company                        = Column(Unicode(255))
    pickup_date                             = Column(DateTime)
    delivered_date                          = Column(DateTime)
    supplier_type                           = Column(Unicode(50))
    status                                  = Column(Unicode(255))
    created_date                            = Column(DateTime)
    modified_date                           = Column(DateTime)
    driver_id                               = Column(Integer)
    driver_name                             = Column(Unicode(255))
    received_clerk_id                       = Column(Integer)
    clerk_received_date                     = Column(DateTime)
    assigned_manager_name                   = Column(Unicode(255))
    supplier_id                             = Column(Integer, ForeignKey('user.id'))

    supplier = relationship("User", back_populates="pickups")
    pickup_details = relationship("PickupTaskDetail", back_populates="pickup_task", cascade="all, delete", passive_deletes=True)

    
class PickupTaskDetail(Base):
    __tablename__ = 'pickup_task_detail'

    id = Column(Integer, primary_key=True)
    public_id = Column(Unicode(50), nullable=False, unique=True, default=generate_uuid)

    quantity                                 = Column(Integer, nullable=False, default=0)
    created_date                             = Column(DateTime)
    modified_date                            = Column(DateTime)

    phone                                    = Column(Unicode(255))
    phone_more                               = Column(Unicode(255))
    district                                 = Column(Unicode(255))
    khoroo                                   = Column(Unicode(255))
    aimag                                    = Column(Unicode(255))
    address                                  = Column(Unicode(255))
    total_amount                             = Column(Integer)
    destination_type                         = Column(Unicode(255))
    
    inventory_id                             = Column(Integer, ForeignKey('inventory.id', ondelete="CASCADE"))
    product_id                               = Column(Integer, ForeignKey('product.id', ondelete="CASCADE"))
    pickup_task_id                           = Column(Integer, ForeignKey('pickup_task.id', ondelete="CASCADE"))

    pickup_task = relationship("PickupTask", back_populates="pickup_details")
    product = relationship("Product", back_populates="product_pickups")


class DriverReturn(Base):
    __tablename__ = 'driver_return'

    id = Column(Integer, primary_key=True)
    public_id = Column(Unicode(50), nullable=False, unique=True, default=generate_uuid)

    is_returned                              = Column(Boolean, default=False)
    is_returned_to_supplier                  = Column(Boolean, default=False)
    delivery_status                          = Column(Unicode(255))
    returned_clerk_name                      = Column(Unicode(255))

    returned_date                            = Column(DateTime)
    created_date                             = Column(DateTime)
    modified_date                            = Column(DateTime)

    driver_name                              = Column(Unicode(255))
    driver_id                                = Column(Integer, ForeignKey('user.id'))
    delivery_id                              = Column(Integer, ForeignKey('delivery.id'))

    driver = relationship("User", back_populates="returns")
    delivery = relationship("Delivery", back_populates="delivery_returns")

    def __repr__(self):
        return f'%s'%(self.delivery.delivery_details)


class AccountantPaymentHistory(Base):
    __tablename__ = 'accountant_payment_history'

    id = Column(Integer, primary_key=True)
    public_id = Column(Unicode(50), nullable=False, unique=True, default=generate_uuid)

    card_amount                              = Column(Integer, nullable=False, default=0)
    cash_amount                              = Column(Integer, nullable=False, default=0)
    remaining_amount                         = Column(Integer, nullable=False, default=0)
    comment                                  = Column(Text)
    delivery_ids                             = Column(Text)
    created_date                             = Column(DateTime)
    modified_date                            = Column(DateTime)
    received_date                            = Column(DateTime)
    payment_of_date                          = Column(DateTime)
    driver_name                              = Column(Unicode(255))
    driver_id                                = Column(Integer)
    accountant_id                            = Column(Integer, ForeignKey('user.id'))

    accountant = relationship("User", back_populates="payment_histories")


class DriverProductReturn(Base):
    __tablename__ = 'driver_product_return'

    id = Column(Integer, primary_key=True)
    public_id = Column(Unicode(50), nullable=False, unique=True, default=generate_uuid)

    is_returned                              = Column(Boolean, default=False)
    returned_clerk_name                      = Column(Unicode(255))
    product_quantity                         = Column(Integer)
    driver_comment                           = Column(Text)

    returned_date                            = Column(DateTime)
    created_date                             = Column(DateTime)
    modified_date                            = Column(DateTime)

    driver_name                              = Column(Unicode(255))
    driver_id                                = Column(Integer, ForeignKey('user.id'))
    delivery_id                              = Column(Integer, ForeignKey('delivery.id'))
    product_id                               = Column(Integer, ForeignKey('product.id'))

    driver = relationship("User", back_populates="substractions")
    delivery = relationship("Delivery", back_populates="delivery_substacts")
    product = relationship("Product", back_populates="product_substracts")


class DropoffTask(Base):
    __tablename__ = 'dropoff_task'

    id = Column(Integer, primary_key=True)
    public_id = Column(Unicode(50), nullable=False, unique=True, default=generate_uuid)

    is_ready                                = Column(Boolean, default=False)
    is_completed                            = Column(Boolean, default=False)
    status                                  = Column(Unicode(255))
    supplier_company                        = Column(Unicode(255))
    delivered_date                          = Column(DateTime)
    created_date                            = Column(DateTime)
    modified_date                           = Column(DateTime)
    driver_id                               = Column(Integer)
    driver_name                             = Column(Unicode(255))
    assigned_manager_id                     = Column(Integer)
    supplier_id                             = Column(Integer, ForeignKey('user.id'))

    supplier = relationship("User", back_populates="dropoffs")
    dropoff_details = relationship("DropoffTaskDetail", back_populates="dropoff_task", cascade="all, delete", passive_deletes=True)

    
class DropoffTaskDetail(Base):
    __tablename__ = 'dropoff_task_detail'

    id = Column(Integer, primary_key=True)
    public_id = Column(Unicode(50), nullable=False, unique=True, default=generate_uuid)

    quantity                                 = Column(Integer, nullable=False, default=0)
    created_date                             = Column(DateTime)
    modified_date                            = Column(DateTime)

    phone                                    = Column(Unicode(255))
    delivery_id                              = Column(Integer)

    product_id                               = Column(Integer, ForeignKey('product.id', ondelete="CASCADE"))
    dropoff_task_id                          = Column(Integer, ForeignKey('dropoff_task.id', ondelete="CASCADE"))

    dropoff_task = relationship("DropoffTask", back_populates="dropoff_details")
    product = relationship("Product", back_populates="product_dropoffs")