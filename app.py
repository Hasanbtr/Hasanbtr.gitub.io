from flask import Flask, request, redirect, render_template, g, session
import os
import sqlite3
import requests

app = Flask(__name__)
# Oturumlar için gizli anahtar belirleme
app.secret_key = os.urandom(24)  # Rastgele bir 24 baytlık gizli anahtar oluşturur

# SQLite veritabanına bağlantı oluştur
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('database.db')
    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

# Google Books API'den kitap kapaklarını alacak fonksiyon
def get_book_cover(book_title):
    # Google Books API kullanarak kitap kapaklarını al
    url = f"https://www.googleapis.com/books/v1/volumes?q={book_title}&maxResults=1"
    response = requests.get(url)
    data = response.json()

    # İlk kitabın kapak resmini al
    if 'items' in data and len(data['items']) > 0:
        volume_info = data['items'][0]['volumeInfo']
        if 'imageLinks' in volume_info:
            cover_url = volume_info['imageLinks']['thumbnail']
            return cover_url

    return None

# Ana sayfa
@app.route('/')
def index():
    # Veritabanından tüm kitapları al
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM books")
    books_data = cursor.fetchall()

    # Kitap verilerini sözlük listesi olarak dönüştür
    books = []
    for book_data in books_data:
        book = {
            'id': book_data[0],
            'title': book_data[1],
            'author': book_data[2],
            'cover': get_book_cover(book_data[1]),  # Kitap başlığını parametre olarak kullanarak kapak al
            # Diğer sütunlar buraya eklenebilir
        }
        books.append(book)

    # Kitapları ana sayfaya gönder
    return render_template('index.html', books=books)

# Üyelik sayfası
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Yeni kullanıcıyı veritabanına ekleyin
        add_user(username, password)
        # Oturumu başlatın ve kullanıcıyı giriş yapmış olarak işaretleyin
        session['logged_in'] = True
        session['username'] = username
        return redirect('/profile')  # Profil sayfasına yönlendirin
    else:
        return render_template('register.html')

# Kullanıcıları veritabanına eklemek için fonksiyon
def add_user(username, password):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

# Kitap ekleme
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        # Formdan gelen verileri al
        title = request.form['title']
        author = request.form['author']
        # Veritabanına kitabı ekle
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO books (title, author) VALUES (?, ?)", (title, author))
        db.commit()
        # Eklenen kitabın ID'sini alabilirsiniz
        book_id = cursor.lastrowid
        # Kitap detayları sayfasına yönlendir
        return redirect(f'/details/{book_id}')  # Kitap eklendikten sonra kitap detayları sayfasına yönlendir
    else:
        return render_template('add_book.html')

# Kitap silme
@app.route('/delete/<int:book_id>', methods=['POST'])
def delete(book_id):
    # Veritabanından kitabı sil
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
    db.commit()
    return redirect('/')  # Kitap silindikten sonra ana sayfaya yönlendir
  
# Kitap güncelleme formu
@app.route('/update/<int:book_id>', methods=['GET', 'POST'])
def update(book_id):
    if request.method == 'POST':
        # Formdan gelen güncellenmiş bilgileri al
        updated_title = request.form['title']
        updated_author = request.form['author']
        # Veritabanında kitabı güncelle
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE books SET title=?, author=? WHERE id=?", (updated_title, updated_author, book_id))
        db.commit()
        # Kitap detayları sayfasına yönlendir
        return redirect(f'/details/{book_id}')  # Kitap güncellendikten sonra kitap detayları sayfasına yönlendir
    else:
        # Veritabanından kitabı al
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM books WHERE id=?", (book_id,))
        book = cursor.fetchone()
        return render_template('update_book.html', book=book)

# Kitap detayları
@app.route('/details/<int:book_id>')
def detail(book_id):
    # Veritabanından kitabı al
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM books WHERE id=?", (book_id,))
    book_data = cursor.fetchone()

    # Kitap verilerini bir sözlüğe dönüştür
    book = {
        'id': book_data[0],
        'title': book_data[1],
        'author': book_data[2],
        # Diğer sütunlar buraya eklenebilir
    }

    # Kitap kapak resmini al
    cover_url = get_book_cover(book['title'])

    # Kitap detayları sayfasına gönder
    return render_template('book_detail.html', book=book, cover_url=cover_url)

# Kullanıcı doğrulama
def authenticate_user(username, password):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cur.fetchone()
    conn.close()
    return user is not None

# Giriş sayfası rota ve görünümü
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate_user(username, password):
            # Başarılı giriş, profil sayfasına yönlendir
            return redirect('/profile')
        else:
            # Hatalı giriş, tekrar giriş sayfasını göster
            return render_template('login.html', error='Invalid username or password')
    else:
        return render_template('login.html', error='')

# Profil sayfası rota ve görünümü
@app.route('/profile')
def profile():
    # Profil sayfası görünümü, bu kısımda kullanıcının profil bilgileri gösterilebilir
    return render_template('profile.html')

if __name__ == '__main__':
    app.run(debug=True)  # Uygulamayı debug modunda çalıştırır
