

from .database  import db

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(15))
    full_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    pin_code = db.Column(db.String(10))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship('Booking', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def create_admin():
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@parking.com',
                full_name='Administrator',
                is_admin=True
            )
            admin.set_password('admin123')  # Change this password in production!
            db.session.add(admin)
            db.session.commit()

    def __repr__(self):
        return f'<User {self.username}>'

class ParkingLot(db.Model):
    __tablename__ = 'parking_lot'
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    total_spots = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    spots = db.relationship('ParkingSpot', backref='lot', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ParkingLot {self.prime_location_name}>'

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spot'
    id = db.Column(db.Integer, primary_key=True)
    spot_number = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(1), default='A')  # 'A' = Available, 'O' = Occupied
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)

    bookings = db.relationship('Booking', backref='spot', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('spot_number', 'lot_id', name='unique_spot_in_lot'),
    )

    def __repr__(self):
        return f'<ParkingSpot {self.spot_number} Lot {self.lot_id}>'

class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)
    check_in = db.Column(db.DateTime, default=datetime.utcnow)
    check_out = db.Column(db.DateTime)
    parking_cost = db.Column(db.Float)
    remarks = db.Column(db.String(255))
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled

    def calculate_amount(self):
        if self.check_out:
            duration = (self.check_out - self.check_in).total_seconds() / 3600
            return round(duration * self.spot.lot.price_per_hour, 2)
        return 0

    def __repr__(self):
        return f'<Booking {self.vehicle_number} Spot {self.spot_id}>'