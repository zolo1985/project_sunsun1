import logging
from datetime import datetime
import pytz
import random
from faker import Faker
from webapp import bcrypt
from webapp.database import Connection
from webapp.models import (Role, TotalInventory, User, ProductColor, Product, ProductSize, Region, District, Aimag)
from webapp import models
from sqlalchemy import func, or_

log = logging.getLogger(__name__)

faker = Faker()

initial_roles = ['supplier1', 'supplier2', 'manager', 'admin', 'driver', 'accountant', 'clerk']
initial_colors = ['Цэнхэр', 'Улаан', 'Ногоон', 'Шар', 'Хар', 'Саарал', 'Ягаан', 'Улбар шар', 'Хөх', 'Бор', 'Чирнээлийн ягаан', 'Өнгөгүй']
initial_sizes = ['XXL', 'XL', 'L', 'M', 'S', 'XS', 'XXS', 'Тодорхойгүй']
initial_delivery_regions = ['Хойд', 'Урд', 'Зүүн', 'Баруун', 'Баруун Хойд', 'Зүүн Хойд', 'Баруун Урд', 'Зүүн Урд']
initial_districts = ['Хан-Уул', 'Баянзүрх', 'Сүхбаатар', 'Налайх', 'Багануур', 'Багахангай', 'Баянгол', 'Сонгинохайрхан', 'Чингэлтэй']
initial_aimags = ['Архангай','Баян-Өлгий','Баянхонгор','Булган','Говь-Алтай','Говьсүмбэр','Дархан-Уул','Дорноговь','Дорнод','Дундговь','Завхан','Орхон','Өвөрхангай','Өмнөговь','Сүхбаатар','Сэлэнгэ','Төв','Увс','Ховд','Хөвсгөл','Хэнтий']
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


def generate_admin():
    connection = Connection()
    hashed_password = bcrypt.generate_password_hash('password')
    user = User(company_name='sunsun',
                firstname='СҮН СҮН',
                lastname='СҮН СҮН',
                email='admin@sunsun.com',
                phone=faker.phone_number(),
                status='verified',
                created_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                modified_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                password=hashed_password)
        
    user_role = connection.query(Role).filter_by(name="admin").first()
    user.roles.append(user_role)
    connection.add(user)

    try:
        connection.commit()
    except Exception as e:
        print(str(e))
        connection.rollback()
        connection.close()
    else:
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


def generate_supplier1_products():
    connection = Connection()
    suppliers = connection.query(models.User).filter(or_(models.User.roles.any(models.Role.name=="supplier1"), models.User.roles.any(models.Role.name=="supplier2"))).all()
    colors = connection.query(ProductColor).all()
    sizes = connection.query(ProductSize).all()

    for i, supplier in enumerate(suppliers):
        for i in range(20):
            product = Product(
                name = faker.word(),
                price = random.randint(1000,10000),
                description = "Product description",
                usage_guide = "Use it for testing",
                created_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                modified_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                image = "645e31ac9c60438c9224943d766fc41b"
            )
            product.sizes.append(random.choice(sizes))
            product.colors.append(random.choice(colors))
            supplier.products.append(product)
            connection.add(product)
            connection.commit()
            
            total_inventory = TotalInventory()
            total_inventory.quantity = 0
            total_inventory.product_id = product.id
            total_inventory.user_id = supplier.id
            total_inventory.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            total_inventory.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            connection.add(total_inventory)
            connection.commit()



def generate_supplier2_orders():
    connection = Connection()
    districts = connection.query(models.District).all()
    suppliers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="supplier2")).all()

    for i, supplier in enumerate(suppliers):
        pickup_task = models.PickupTask()
        pickup_task.supplier_company = supplier.company_name
        pickup_task.is_ready = True
        pickup_task.status = "waiting"
        pickup_task.supplier_type = "supplier2"
        pickup_task.supplier_id = supplier.id
        pickup_task.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
        pickup_task.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

        supplier.pickups.append(pickup_task)

        for i in range(10):
            pickup_task_detail = models.PickupTaskDetail()
            pickup_task_detail.phone = faker.phone_number()
            pickup_task_detail.phone_more = faker.phone_number()
            pickup_task_detail.district = random.choice(districts)
            pickup_task_detail.khoroo = random.randint(1,15)
            pickup_task_detail.address = faker.address()
            pickup_task_detail.total_amount = random.randint(10000,100000)
            pickup_task_detail.destination_type = "local"
            pickup_task_detail.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            pickup_task_detail.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

            pickup_task.pickup_details.append(pickup_task_detail)

    connection.commit()



def generate_supplier1_inventories():
    connection = Connection()
    suppliers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="supplier1")).all()

    for i, supplier in enumerate(suppliers):
        pickup_task = models.PickupTask()
        pickup_task.supplier_company = supplier.company_name
        pickup_task.is_ready = True
        pickup_task.status = "waiting"
        pickup_task.supplier_type = "supplier1"
        pickup_task.supplier_id = supplier.id
        pickup_task.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
        pickup_task.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

        supplier.pickups.append(pickup_task)

        supplier_products = connection.query(models.Product).filter(models.Product.supplier_id==supplier.id).all()

        for i, supplier_product in enumerate(supplier_products):
            pickup_task_detail = models.PickupTaskDetail()
            pickup_task_detail.quantity = random.randint(100,500),
            pickup_task_detail.product_id = int(supplier_product.id)
            pickup_task_detail.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            pickup_task_detail.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

            pickup_task.pickup_details.append(pickup_task_detail)

    connection.commit()

    

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
        generate_admin()
        generate_clerks(2)
        generate_managers(2)
        generate_drivers(10)
        generate_accountants(2)

    @app.cli.command('initial-data')
    def initial_data():
        generate_admin()
        generate_roles()
        generate_regions()
        generate_districts()
        generate_aimags()

    @app.cli.command('test-suppliers')
    def test_suppliers():
        generate_accounts(10)
        generate_supplier1_products()
        generate_supplier2_orders()
        generate_supplier1_inventories()

    @app.cli.command('reset-data')
    def reset_data():
        reset_database_data()

    @app.cli.command('gen-admin')
    def gen_admin():
        generate_admin()