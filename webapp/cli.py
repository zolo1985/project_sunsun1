import logging
from datetime import datetime
import pytz

from faker import Faker

from webapp import bcrypt
from webapp.database import Connection
from webapp.models import (Role, TotalInventory, User, ProductColor, Product, ProductSize, Region, District, Aimag, PaymentType)

log = logging.getLogger(__name__)

faker = Faker()

initial_roles = ['supplier1', 'supplier2', 'manager', 'admin', 'driver', 'accountant', 'clerk']
initial_colors = ['Цэнхэр', 'Улаан', 'Ногоон', 'Шар', 'Хар', 'Саарал', 'Ягаан', 'Улбар шар', 'Хөх', 'Бор', 'Чирнээлийн ягаан', 'undefined']
initial_sizes = ['XXL', 'XL', 'L', 'M', 'S', 'XS', 'XXS', 'Тодорхойгүй']
initial_delivery_regions = ['Хойд', 'Урд', 'Зүүн', 'Баруун', 'Баруун Хойд', 'Зүүн Хойд', 'Баруун Урд', 'Зүүн Урд']
initial_artworks = [('webapp/static/images/menu-bg.jpg')]

initial_districts = ['Хан-Уул', 'Баянзүрх', 'Сүхбаатар', 'Налайх', 'Багануур', 'Багахангай', 'Баянгол', 'Сонгинохайрхан', 'Чингэлтэй']
initial_aimags = ['Архангай','Баян-Өлгий','Баянхонгор','Булган','Говь-Алтай','Говьсүмбэр','Дархан-Уул','Дорноговь','Дорнод','Дундговь','Завхан','Орхон','Өвөрхангай','Өмнөговь','Сүхбаатар','Сэлэнгэ','Төв','Увс','Ховд','Хөвсгөл','Хэнтий']
initial_payment_types = ['Үндсэн үнэ','Хүргэлт орсон', 'Төлбөр авахгүй']

initial_delivery_status = ['started', 'completed', 'cancelled', 'postphoned', 'assigned', 'unassigned']

def generate_roles():
    roles = list()
    connection = Connection()
    for rolename in initial_roles:
        role = connection.query(Role).filter_by(name=rolename).first()
        if role:
            roles.append(role)
            continue
        role = Role(name=rolename)
        roles.append(role)
        connection.add(role)
        try:
            connection.commit()
            connection.close()
        except Exception as e:
            log.error("Erro inserting role: %s, %s" % (str(role), e))
            connection.rollback()
            connection.close()
    return roles



def generate_districts():
    districts = list()
    connection = Connection()
    for districtname in initial_districts:
        district = connection.query(District).filter_by(name=districtname).first()
        if district:
            districts.append(district)
            continue
        district = District(name=districtname)
        districts.append(district)
        connection.add(district)
        try:
            connection.commit()
            connection.close()
        except Exception as e:
            log.error("Erro inserting district: %s, %s" % (str(district), e))
            connection.rollback()
            connection.close()
    return districts


def generate_aimags():
    aimags = list()
    connection = Connection()
    for aimagname in initial_aimags:
        aimag = connection.query(Aimag).filter_by(name=aimagname).first()
        if aimag:
            aimags.append(aimag)
            continue
        aimag = Aimag(name=aimagname)
        aimags.append(aimag)
        connection.add(aimag)
        try:
            connection.commit()
            connection.close()
        except Exception as e:
            log.error("Erro inserting aimag: %s, %s" % (str(aimag), e))
            connection.rollback()
            connection.close()
    return aimags


def generate_payment_types():
    payment_types = list()
    connection = Connection()
    for paymenttypename in initial_payment_types:
        paymenttype = connection.query(PaymentType).filter_by(name=paymenttypename).first()
        if paymenttype:
            payment_types.append(paymenttype)
            continue
        paymenttype = PaymentType(
            name = paymenttypename,
            amount = 0)
        payment_types.append(paymenttype)
        connection.add(paymenttype)
        try:
            connection.commit()
            connection.close()
        except Exception as e:
            log.error("Erro inserting paymenttype: %s, %s" % (str(paymenttype), e))
            connection.rollback()
            connection.close()
    return payment_types



def generate_regions():
    regions = list()
    connection = Connection()
    for regionname in initial_delivery_regions:
        region = connection.query(Region).filter_by(name=regionname).first()
        if region:
            regions.append(region)
            continue
        region = Region(name=regionname)
        regions.append(region)
        connection.add(region)
        try:
            connection.commit()
            connection.close()
        except Exception as e:
            log.error("Erro inserting region: %s, %s" % (str(region), e))
            connection.rollback()
            connection.close()
    return regions


def generate_accounts(n):
    connection = Connection()
    for i in range(n):
        hashed_password = bcrypt.generate_password_hash('password')
        user = User(company_name='company%s'%(i), 
                    firstname='Төрөө%s'%(i),
                    lastname='Төрөө%s'%(i),
                    email='company%s@sunsun.com'%(i), 
                    phone=faker.phone_number(),
                    status='verified',
                    created_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                    modified_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                    password=hashed_password)
            
        user_role = connection.query(Role).filter_by(name="supplier1").first()
        user.roles.append(user_role)
        connection.add(user)
        connection.commit()
        connection.close()

def generate_managers(n):
    connection = Connection()
    for i in range(n):
        hashed_password = bcrypt.generate_password_hash('password')
        user = User(company_name='sunsun%s'%(i), 
                    firstname='Баясаа%s'%(i),
                    lastname='Баясаа%s'%(i),
                    email='manager%s@sunsun.com'%(i), 
                    phone=faker.phone_number(),
                    status='verified',
                    created_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                    modified_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                    password=hashed_password)
            
        user_role = connection.query(Role).filter_by(name="manager").first()
        user.roles.append(user_role)
        connection.add(user)
        connection.commit()
        connection.close()


def generate_accountants(n):
    connection = Connection()
    for i in range(n):
        hashed_password = bcrypt.generate_password_hash('password')
        user = User(company_name='accountant%s'%(i), 
                    firstname='Өлзий%s'%(i),
                    lastname='Өлзий%s'%(i),
                    email='accountant%s@sunsun.com'%(i), 
                    phone=faker.phone_number(),
                    status='verified',
                    created_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                    modified_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                    password=hashed_password)
            
        user_role = connection.query(Role).filter_by(name="accountant").first()
        user.roles.append(user_role)
        connection.add(user)
        connection.commit()
        connection.close()


def generate_clerks(n):
    connection = Connection()
    for i in range(n):
        hashed_password = bcrypt.generate_password_hash('password')
        user = User(company_name='clerk%s'%(i),
                    firstname='Сараа%s'%(i),
                    lastname='Сараа%s'%(i),
                    email='clerk%s@sunsun.com'%(i),
                    phone=faker.phone_number(),
                    status='verified',
                    created_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                    modified_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                    password=hashed_password)
            
        user_role = connection.query(Role).filter_by(name="clerk").first()
        user.roles.append(user_role)
        connection.add(user)
        connection.commit()
        connection.close()


def generate_drivers(n):
    connection = Connection()
    for i in range(n):
        hashed_password = bcrypt.generate_password_hash('password')
        user = User(company_name='driver%s'%(i), 
                    firstname='Галаа%s'%(i),
                    lastname='Галаа%s'%(i), 
                    email='driver%s@sunsun.com'%(i), 
                    phone=faker.phone_number(),
                    status='verified',
                    created_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                    modified_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                    password=hashed_password)
            
        user_role = connection.query(Role).filter_by(name="driver").first()
        user.roles.append(user_role)
        connection.add(user)
        connection.commit()
        connection.close()

def generate_supplier2(n):
    connection = Connection()
    for i in range(n):
        hashed_password = bcrypt.generate_password_hash('password')
        user = User(company_name='supplier2%s'%(i), 
                    firstname='Галаа1%s'%(i),
                    lastname='Галаа1%s'%(i), 
                    email='supplier2%s@sunsun.com'%(i), 
                    phone=faker.phone_number(),
                    status='verified',
                    created_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                    modified_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                    password=hashed_password)
            
        user_role = connection.query(Role).filter_by(name="supplier2").first()
        user.roles.append(user_role)
        connection.add(user)
        connection.commit()
        connection.close()

def generate_colors():
    colors = list()
    connection = Connection()
    for colorname in initial_colors:
        color = connection.query(ProductColor).filter_by(name=colorname).first()
        if color:
            colors.append(color)
            continue
        color = ProductColor(name=colorname)
        colors.append(color)
        connection.add(color)
        try:
            connection.commit()
            connection.close()
        except Exception as e:
            log.error("Erro inserting role: %s, %s" % (str(color), e))
            connection.rollback()
            connection.close()
    return colors


def generate_sizes():
    sizes = list()
    connection = Connection()
    for sizename in initial_sizes:
        size = connection.query(ProductSize).filter_by(name=sizename).first()
        if size:
            sizes.append(size)
            continue
        size = ProductSize(name=sizename)
        sizes.append(size)
        connection.add(size)
        try:
            connection.commit()
            connection.close()
        except Exception as e:
            log.error("Erro inserting role: %s, %s" % (str(size), e))
            connection.rollback()
            connection.close()
    return sizes


def generate_red_m_products(n):
    connection = Connection()
    fetch_account_type1 = connection.query(User).filter_by(company_name="company0").first()
    colors = connection.query(ProductColor).all()
    sizes = connection.query(ProductSize).all()
    for i in range(n):
        product = Product(
            name = faker.word(),
            price = 10000,
            description = "Product description",
            usage_guide = "Use it for testing",
            created_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
            modified_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
            # image = add_and_resize_image_from_local_path1(os.path.abspath(random.choice(initial_artworks)))
        )
        product.sizes.append(sizes[i])
        product.colors.append(colors[i])
        fetch_account_type1.products.append(product)
        connection.add(product)
        connection.commit()

        total_inventory = TotalInventory()
        total_inventory.quantity = 0
        total_inventory.product_id = product.id
        total_inventory.user_id = fetch_account_type1.id
        total_inventory.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
        total_inventory.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
        connection.add(total_inventory)
        connection.commit()
        connection.close()

def generate_blue_xl_products(n):
    connection = Connection()
    fetch_account_type1 = connection.query(User).filter_by(company_name="company0").first()
    colors = connection.query(ProductColor).all()
    sizes = connection.query(ProductSize).all()
    for i in range(n):
        product = Product(
            name = "product%s"%(i+5),
            price = 10000,
            description = "Product description",
            usage_guide = "Use it for testing",
            created_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
            modified_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
            # image = add_and_resize_image_from_local_path1(os.path.abspath(random.choice(initial_artworks)))
        )
        product.sizes.append(sizes[i])
        product.colors.append(colors[i])
        fetch_account_type1.products.append(product)
        connection.add(product)
        connection.commit()
        
        total_inventory = TotalInventory()
        total_inventory.quantity = 0
        total_inventory.product_id = product.id
        total_inventory.user_id = fetch_account_type1.id
        total_inventory.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
        total_inventory.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
        connection.add(total_inventory)
        connection.commit()
        connection.close()

        

def reset_database_data():
    connection = Connection()
    connection.execute("DROP DATABASE sunsundatabase1")
    connection.execute("CREATE DATABASE sunsundatabase1 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    connection.close()

def register(app):
    @app.cli.command('test-data')
    def test_data():
        generate_roles()
        generate_colors()
        generate_sizes()
        generate_regions()
        generate_districts()
        generate_aimags()
        generate_payment_types()
        generate_clerks(2)
        generate_accounts(10)
        generate_managers(2)
        generate_drivers(10)
        generate_accountants(2)
        generate_red_m_products(5)
        generate_blue_xl_products(5)
        generate_supplier2(2)

    @app.cli.command('initial-data')
    def initial_data():
        generate_roles()
        generate_regions()
        generate_districts()
        generate_aimags()
        generate_payment_types()
        generate_accounts(2)
        generate_supplier2(2)

    @app.cli.command('reset-data')
    def reset_data():
        reset_database_data()