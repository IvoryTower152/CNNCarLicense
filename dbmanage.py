from dbbase import Car, engine
from sqlalchemy.orm import sessionmaker
import datetime


# 对出入高速站车辆进行管理
def manage_car(str_lic, str_type):
    str_result = ''
    str_price = ''
    # 由于车牌是区分汽车的重要标识符
    # 不存在有相同车牌的汽车，即使车牌颜色不同也不可能
    # 因此从车牌在数据库中的记录来判断其是进入高速还是驶出高速
    Session = sessionmaker(engine)
    db_session = Session()
    # 搜索所有车牌为指定车牌且没有驶出时间的记录
    # 若有(应是有且只有1条)则说明其仍在高速上，若没有(返回0条)说明其是进入高速
    cars = db_session.query(Car).filter(Car.license == str_lic, Car.out_time == None).all()
    # 在高速上再次来到收费站，说明是下站行为，在其纪录上追加驶出时间
    if len(cars) == 1:
        car = cars[0]
        dateTime_p = datetime.datetime.now()
        str_date = datetime.datetime.strftime(dateTime_p, '%Y-%m-%d %H:%M:%S')
        res = db_session.query(Car).filter(Car.id == car.id).update({'out_time': str_date})
        str_result = '离开高速'
        car_type = car.type
        if car_type == '蓝色车牌':
            str_price = '50￥'
        elif car_type == '黄色车牌':
            str_price = '100￥'
    # 进入高速公路，将其车辆信息加入到数据库中
    elif len(cars) == 0:
        dateTime_p = datetime.datetime.now()
        str_date = datetime.datetime.strftime(dateTime_p, '%Y-%m-%d %H:%M:%S')
        car = Car(license=str_lic, type=str_type, in_time=str_date)
        db_session.add(car)
        str_result = '驶入高速'
        str_price = '---￥'
    db_session.commit()
    db_session.close()
    return str_result, str_price


if __name__ == '__main__':
    str_result = manage_car('浙L31900', '蓝色车牌')
    print(str_result)