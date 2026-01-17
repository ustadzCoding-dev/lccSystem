from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import xlsxwriter
from io import BytesIO
import json
import os

app = Flask(__name__)

# Load konfigurasi berdasarkan environment
env = os.environ.get('FLASK_ENV', 'development')
from config import config
app.config.from_object(config[env])

db = SQLAlchemy(app)

# Pastikan folder instance ada
os.makedirs(app.instance_path, exist_ok=True)

# Model untuk menyimpan konfigurasi soal per babak
class BabakConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    babak = db.Column(db.Integer, nullable=False)
    jumlah_soal = db.Column(db.Integer, default=5)
    nama_babak = db.Column(db.String(100), default="Babak") # Untuk nama kustom babak
    active = db.Column(db.Boolean, default=True) # Untuk mengaktifkan/nonaktifkan babak

    @staticmethod
    def get_active_configs():
        return BabakConfig.query.filter_by(active=True).order_by(BabakConfig.babak).all()

    @staticmethod
    def get_max_babak():
        max_config = BabakConfig.query.order_by(BabakConfig.babak.desc()).first()
        return max_config.babak if max_config else 0

# Model untuk menyimpan nilai soal
class SoalNilai(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    babak = db.Column(db.Integer, nullable=False)
    nomor_soal = db.Column(db.Integer, nullable=False)
    nilai = db.Column(db.Integer, default=0)

# Model untuk Tim
class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    member1 = db.Column(db.String(100))
    member2 = db.Column(db.String(100))
    member3 = db.Column(db.String(100))
    score_babak1 = db.Column(db.Integer, default=0)
    score_babak2 = db.Column(db.Integer, default=0)
    score_babak3 = db.Column(db.Integer, default=0)
    total_score = db.Column(db.Integer, default=0)
    nilai_soal = db.relationship('SoalNilai', backref='team', lazy=True)

    def get_nilai_soal(self, babak, nomor_soal):
        nilai = SoalNilai.query.filter_by(
            team_id=self.id,
            babak=babak,
            nomor_soal=nomor_soal
        ).first()
        return nilai.nilai if nilai else 0

    def update_babak_score(self, babak):
        total = 0
        nilai_soal = SoalNilai.query.filter_by(team_id=self.id, babak=babak).all()
        for nilai in nilai_soal:
            total += nilai.nilai

        if babak == 1:
            self.score_babak1 = total
        elif babak == 2:
            self.score_babak2 = total
        elif babak == 3:
            self.score_babak3 = total

        self.total_score = self.score_babak1 + self.score_babak2 + self.score_babak3
        db.session.commit()

@app.route('/')
def index():
    teams = Team.query.all()
    configs = BabakConfig.get_active_configs()
    
    # Jika belum ada konfigurasi, buat default
    if not configs:
        for babak in range(1, 4):
            config = BabakConfig(babak=babak, jumlah_soal=5)
            db.session.add(config)
        db.session.commit()
        configs = BabakConfig.get_active_configs()
    
    return render_template('index.html', teams=teams, configs=configs)

@app.route('/update-babak-config', methods=['POST'])
def update_babak_config():
    try:
        configs = BabakConfig.get_active_configs()
        for config in configs:
            jumlah_soal = request.form.get(f'babak{config.babak}')
            if jumlah_soal:
                config.jumlah_soal = int(jumlah_soal)
        db.session.commit()
        flash('Konfigurasi babak berhasil diupdate', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('index'))

@app.route('/update-score/<int:team_id>/<int:babak>', methods=['POST'])
def update_score(team_id, babak):
    team = Team.query.get_or_404(team_id)
    config = BabakConfig.query.filter_by(babak=babak).first()
    
    if not config:
        flash('Konfigurasi babak tidak ditemukan', 'danger')
        return redirect(url_for('index'))
    
    for i in range(1, config.jumlah_soal + 1):
        nilai = int(request.form.get(f'nilai{i}', 0))
        soal_nilai = SoalNilai.query.filter_by(
            team_id=team_id,
            babak=babak,
            nomor_soal=i
        ).first()
        
        if soal_nilai:
            soal_nilai.nilai = nilai
        else:
            soal_nilai = SoalNilai(
                team_id=team_id,
                babak=babak,
                nomor_soal=i,
                nilai=nilai
            )
            db.session.add(soal_nilai)
    
    db.session.commit()
    team.update_babak_score(babak)
    flash('Nilai berhasil diupdate', 'success')
    return redirect(url_for('index'))

@app.route('/reset-babak/<int:team_id>/<int:babak>')
def reset_babak(team_id, babak):
    try:
        SoalNilai.query.filter_by(team_id=team_id, babak=babak).delete()
        team = Team.query.get(team_id)
        if team:
            team.update_babak_score(babak)
        db.session.commit()
        flash(f'Nilai babak {babak} berhasil direset', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('index'))

@app.route('/add-team', methods=['POST'])
def add_team():
    try:
        name = request.form.get('name')
        member1 = request.form.get('member1')
        member2 = request.form.get('member2')
        member3 = request.form.get('member3')
        
        team = Team(name=name, member1=member1, member2=member2, member3=member3)
        db.session.add(team)
        db.session.commit()
        flash('Tim berhasil ditambahkan', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('index'))

@app.route('/delete-team/<int:team_id>')
def delete_team(team_id):
    try:
        team = Team.query.get_or_404(team_id)
        SoalNilai.query.filter_by(team_id=team_id).delete()
        db.session.delete(team)
        db.session.commit()
        flash('Tim berhasil dihapus', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('index'))

@app.route('/edit-team/<int:team_id>', methods=['GET', 'POST'])
def edit_team(team_id):
    team = Team.query.get_or_404(team_id)
    if request.method == 'POST':
        try:
            team.name = request.form.get('name')
            team.member1 = request.form.get('member1')
            team.member2 = request.form.get('member2')
            team.member3 = request.form.get('member3')
            db.session.commit()
            flash('Tim berhasil diupdate', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    return render_template('edit_team.html', team=team)

@app.route('/export-excel')
def export_excel():
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    # Format
    header_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#D9D9D9',
        'border': 1
    })

    cell_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })

    # Headers
    headers = ['No', 'Nama Tim', 'Anggota 1', 'Anggota 2', 'Anggota 3', 
              'Skor Babak 1', 'Skor Babak 2', 'Skor Babak 3', 'Total Skor']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)

    # Data
    teams = Team.query.order_by(Team.total_score.desc()).all()
    for row, team in enumerate(teams, 1):
        data = [
            row,
            team.name,
            team.member1,
            team.member2,
            team.member3,
            team.score_babak1,
            team.score_babak2,
            team.score_babak3,
            team.total_score
        ]
        for col, value in enumerate(data):
            worksheet.write(row, col, value, cell_format)

    # Adjust column width
    worksheet.set_column('A:A', 5)   # No
    worksheet.set_column('B:B', 20)  # Nama Tim
    worksheet.set_column('C:E', 15)  # Anggota
    worksheet.set_column('F:I', 12)  # Skor

    workbook.close()
    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='hasil_lomba.xlsx'
    )

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    if query:
        # Mencari tim berdasarkan nama tim atau nama anggota
        teams = Team.query.filter(
            db.or_(
                db.func.lower(Team.name).contains(query),
                db.func.lower(Team.member1).contains(query),
                db.func.lower(Team.member2).contains(query),
                db.func.lower(Team.member3).contains(query)
            )
        ).all()
    else:
        teams = Team.query.all()
    
    configs = BabakConfig.get_active_configs()
    return render_template('index.html', teams=teams, configs=configs)

@app.route('/manage-babak', methods=['GET'])
def manage_babak():
    configs = BabakConfig.query.order_by(BabakConfig.babak).all()
    return render_template('manage_babak.html', configs=configs)

@app.route('/add-babak', methods=['POST'])
def add_babak():
    try:
        max_babak = BabakConfig.get_max_babak()
        new_babak = max_babak + 1
        nama_babak = request.form.get('nama_babak', f'Babak {new_babak}')
        jumlah_soal = int(request.form.get('jumlah_soal', 5))
        
        config = BabakConfig(
            babak=new_babak,
            nama_babak=nama_babak,
            jumlah_soal=jumlah_soal,
            active=True
        )
        db.session.add(config)
        db.session.commit()
        flash(f'Babak baru "{nama_babak}" berhasil ditambahkan', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('manage_babak'))

@app.route('/toggle-babak/<int:babak_id>', methods=['POST'])
def toggle_babak(babak_id):
    try:
        config = BabakConfig.query.get_or_404(babak_id)
        config.active = not config.active
        db.session.commit()
        status = "diaktifkan" if config.active else "dinonaktifkan"
        flash(f'Babak "{config.nama_babak}" berhasil {status}', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('manage_babak'))

@app.route('/update-nama-babak/<int:babak_id>', methods=['POST'])
def update_nama_babak(babak_id):
    try:
        config = BabakConfig.query.get_or_404(babak_id)
        nama_baru = request.form.get('nama_babak')
        if nama_baru:
            config.nama_babak = nama_baru
            db.session.commit()
            flash(f'Nama babak berhasil diubah menjadi "{nama_baru}"', 'success')
        else:
            flash('Nama babak tidak boleh kosong', 'danger')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('manage_babak'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Buat konfigurasi default jika belum ada
        for babak in range(1, 4):
            config = BabakConfig.query.filter_by(babak=babak).first()
            if not config:
                config = BabakConfig(babak=babak, jumlah_soal=5)
                db.session.add(config)
        db.session.commit()
    app.run(debug=True)
