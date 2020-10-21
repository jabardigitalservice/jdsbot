Bot groupware JDS
-----------------

Bot telegram untuk submit groupware dari group evidence telegram

![Code Climate maintainability](https://img.shields.io/codeclimate/maintainability/jabardigitalservice/jdsbot)
![Code Climate technical debt](https://img.shields.io/codeclimate/tech-debt/jabardigitalservice/jdsbot?style=plastic)

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
  uvicorn server:app --port 8000
  ```
4. Khusus running tanpa docker, setup dahulu tabel: masuk dulu ke environment
  - python `. .venv/bin/activate`

  kemudian run command-command berikut:

  ```
  python
  >>> import models.user as user
  >>> import models.chat_history as chat_history
  >>> user.create_table()
  >>> chat_history.create_table()
  ```

## setup webhook di lokal
1. buat dulu bot baru, siapkan tokennya
2. masukkan token ke file .env
3. siapkan security token untuk mengakses aplikasi kita, simpan ke file .env
3. jalankan api bot di lokal
4. dapatkan alamat publik komputer kita. bisa pakai ngrok atau memanfaatkan layanan seperti localhost.run . contoh:

  `ssh -R 80:localhost:8000 ssh.localhost.run`

  setelah berjalan kita akan mendapatkan alamat publik temporary dari komputer kita. misal: http://something-123456.localhost.run
5. dengan cara seperti langkah nomor 4 di atas, jalankan command berikut:
  ```
  python
  >>> import models.bot as bot
  >>> bot.run_command('/getme')
  >>> bot.run_command('/setwebhook', {'url': 'https://something-123456.localhost.run/telegram/1'})
  >>> bot.run_command('/getwebhookinfo')
  ```

  perhatikan, ubah http di url jadi https, tambahkan path '/telegram/<kode token>' di akhir

## Todo Fitur
- [x] reply gambar dan input groupware dengan format tertentu
- [x] jadikan webhook (gak pakai loop polling)
  - [x] deploy di caprover
- [x] tambah alias field yang lebih user friendly
- [x] command `/tambah`
- [x] tambah peserta dengan mention user telegram (bukan username groupware)
- [ ] pakai API dedicated utk input user (gak pakai login manual)
- [x] buat agar nama project jadi tidak case sensitive
