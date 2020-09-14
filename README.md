Bot groupware JDS
-----------------

Bot telegram untuk submit groupware dari group evidence telegram

## Cara setup

1. Copy file example.env menjadi .env, isikan variabel yang ada
2. Siapkan database, isikan setting koneksi di variabel DATABASE_URL di file .env
3. Running local:
  - dengan docker compose, cukup run `docker-compose up`
  - setup manual python:

  ```
  python3 -m venv .venv
  . .venv/bin/activate
  python -m pip install --upgrade pip
  pip install -r requirements.txt
  gunicorn server:app --bind 0.0.0.0:8000
  ```
4. setup tabel: masuk dulu ke environment
  - docker : `docker-compose exec api sh`
  - python `. .venv/bin/activate`

  kemudian run command-command berikut:

  ```
  python
  >>> import models.user as user
  >>> import models.chat_history as chat_history
  >>> user.create_table()
  >>> chat_history.create_table()
  ```

## Todo Fitur
- [x] reply gambar dan input groupware dengan format tertentu
- [x] jadikan webhook (gak pakai loop polling)
  - [x] deploy di caprover
- [x] tambah alias field yang lebih user friendly
- [ ] command `/tambah`
- [x] tambah peserta dengan mention user telegram (bukan username groupware)
- [ ] pakai API dedicated utk input user (gak pakai login manual)
- [x] buat agar nama project jadi tidak case sensitive
