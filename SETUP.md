# Summon CRM — Full Stack Setup Guide

Panduan lengkap untuk setup **Summon CRM** beserta seluruh modul terintegrasi (Drive, Helpdesk, Insights, Lending, Telephony, Omnichannel Chat).

---

## Table of Contents

- [Arsitektur Project](#arsitektur-project)
- [Prerequisites](#prerequisites)
- [Cara 1: Setup Otomatis dengan apps.json](#cara-1-setup-otomatis-dengan-appsjson)
- [Cara 2: Setup Manual Step-by-Step](#cara-2-setup-manual-step-by-step)
- [Menjalankan Development Server](#menjalankan-development-server)
- [Frontend Development](#frontend-development)
- [Daftar Modul & Fitur](#daftar-modul--fitur)
- [FAQ](#faq)

---

## Arsitektur Project

```
frappe-crm/                  ← Repo ini (push ke GitHub)
├── crm/                     ← Backend (Frappe doctypes, API, hooks)
├── frontend/                ← Frontend (Vue.js + Frappe UI)
├── apps.json                ← Manifest semua app yang dibutuhkan
├── SETUP.md                 ← File ini
└── README.md

my-frappe-bench/             ← Frappe Bench (JANGAN push ke GitHub)
├── apps/
│   ├── crm → symlink ke frappe-crm/
│   ├── frappe/              ← Framework core
│   ├── erpnext/             ← ERP module
│   ├── drive/               ← File management
│   ├── helpdesk/            ← Ticketing system
│   ├── insights/            ← Data analytics
│   ├── lending/             ← Loan management
│   ├── telephony/           ← Call integration
│   └── clefincode_chat/     ← Omnichannel chat (WhatsApp, dll)
├── sites/                   ← Site config & database
├── env/                     ← Python virtual environment
└── logs/                    ← Log files
```

> **Penting:** Hanya folder `frappe-crm/` yang perlu di-push ke GitHub. Folder `my-frappe-bench/` adalah environment runtime yang di-setup ulang menggunakan panduan ini.

---

## Prerequisites

Pastikan software berikut sudah terinstall di mesin kamu:

| Software       | Versi Minimum | Cek Instalasi            |
| -------------- | ------------- | ------------------------ |
| Python         | 3.10+         | `python3 --version`      |
| Node.js        | 18+           | `node --version`         |
| MariaDB        | 10.6+         | `mariadb --version`      |
| Redis          | 6+            | `redis-server --version` |
| Git            | 2.x           | `git --version`          |
| yarn           | 1.x           | `yarn --version`         |
| wkhtmltopdf    | 0.12.6+       | `wkhtmltopdf --version`  |
| Bench CLI      | 5.x           | `bench --version`        |

### Install Bench CLI (jika belum ada)

```bash
pip3 install frappe-bench
```

> Untuk panduan instalasi lengkap prerequisites per OS, lihat:
> [Frappe Framework Installation Guide](https://docs.frappe.io/framework/user/en/installation)

---

## Cara 1: Setup Otomatis dengan apps.json

Cara tercepat. Satu command untuk init bench + download semua app sekaligus.

### Step 1 — Clone repo CRM

```bash
git clone https://github.com/withsummon/crm-summon.git frappe-crm
cd frappe-crm
```

### Step 2 — Init Frappe Bench dengan apps.json

```bash
cd ..
bench init my-frappe-bench \
  --frappe-branch version-15 \
  --skip-redis-config-generation \
  --apps_path ./frappe-crm/apps.json
```

> **Catatan:** Proses ini akan mengunduh semua app yang terdaftar di `apps.json`. Pastikan koneksi internet stabil karena ukuran total cukup besar.

### Step 3 — Link repo CRM ke bench (jika belum ter-link)

Secara default bench akan clone CRM dari remote. Jika kamu ingin menggunakan folder `frappe-crm` lokal yang sudah kamu clone:

```bash
cd my-frappe-bench

# Hapus folder crm yang di-clone oleh bench
rm -rf apps/crm

# Buat symlink ke repo lokal kamu
ln -s ../../frappe-crm apps/crm
```

### Step 4 — Buat site baru

```bash
bench new-site crm.localhost \
  --mariadb-root-password <ROOT_PASSWORD_MARIADB> \
  --admin-password admin \
  --no-mariadb-socket
```

### Step 5 — Install semua app ke site

```bash
bench --site crm.localhost install-app erpnext
bench --site crm.localhost install-app lending
bench --site crm.localhost install-app drive
bench --site crm.localhost install-app telephony
bench --site crm.localhost install-app helpdesk
bench --site crm.localhost install-app insights
bench --site crm.localhost install-app clefincode_chat
bench --site crm.localhost install-app crm
```

### Step 6 — Set sebagai default site

```bash
bench use crm.localhost
```

### Step 7 — Jalankan!

```bash
bench start
```

Akses di browser: **http://crm.localhost:8000**

- Username: `Administrator`
- Password: `admin` (atau sesuai yang kamu set di Step 4)

---

## Cara 2: Setup Manual Step-by-Step

Jika kamu ingin kontrol penuh, setup satu per satu.

### Step 1 — Clone repo CRM

```bash
git clone https://github.com/withsummon/crm-summon.git frappe-crm
```

### Step 2 — Init Frappe Bench

```bash
bench init my-frappe-bench --frappe-branch version-15
cd my-frappe-bench
```

### Step 3 — Download semua app

```bash
# Core
bench get-app erpnext --branch version-15

# Modul tambahan
bench get-app drive --branch main
bench get-app helpdesk --branch main
bench get-app insights --branch version-3
bench get-app lending --branch version-15
bench get-app telephony --branch develop
bench get-app https://github.com/clefincode/clefincode_chat.git --branch develop
```

### Step 4 — Link CRM dari repo lokal

```bash
# Symlink repo CRM kamu (bukan clone dari remote)
ln -s ../../frappe-crm apps/crm

# Daftarkan CRM di bench
echo "crm" >> sites/apps.txt
```

### Step 5 — Install dependencies CRM

```bash
cd apps/crm
pip install -e .
cd ../..
```

### Step 6 — Buat site dan install app

```bash
bench new-site crm.localhost \
  --mariadb-root-password <ROOT_PASSWORD_MARIADB> \
  --admin-password admin \
  --no-mariadb-socket

# Install semua app (urutan penting!)
bench --site crm.localhost install-app erpnext
bench --site crm.localhost install-app lending
bench --site crm.localhost install-app drive
bench --site crm.localhost install-app telephony
bench --site crm.localhost install-app helpdesk
bench --site crm.localhost install-app insights
bench --site crm.localhost install-app clefincode_chat
bench --site crm.localhost install-app crm

bench use crm.localhost
```

### Step 7 — Jalankan

```bash
bench start
```

---

## Menjalankan Development Server

Setelah setup selesai, untuk development sehari-hari:

```bash
cd my-frappe-bench
bench start
```

Ini akan menjalankan:
- **Frappe web server** di `http://crm.localhost:8000`
- **Socket.IO** untuk realtime updates
- **Redis** untuk cache dan queue
- **Background workers** untuk async jobs

### Enable Developer Mode

```bash
bench --site crm.localhost set-config developer_mode 1
bench clear-cache
```

---

## Frontend Development

Untuk develop frontend CRM dengan hot-reload:

```bash
cd my-frappe-bench/apps/crm   # atau langsung cd frappe-crm
yarn install
yarn dev
```

Frontend dev server berjalan di `http://crm.localhost:8080` dengan hot module replacement (HMR).

> **Catatan:** `bench start` harus tetap berjalan di terminal terpisah karena frontend membutuhkan backend API dari Frappe.

---

## Daftar Modul & Fitur

Berikut semua modul yang terinstall dan fitur yang disediakan:

| Modul              | Repository                                        | Branch      | Fitur Utama                                       |
| ------------------ | ------------------------------------------------- | ----------- | ------------------------------------------------- |
| **Frappe**         | [frappe/frappe](https://github.com/frappe/frappe)                     | version-15  | Framework core, user management, permissions       |
| **ERPNext**        | [frappe/erpnext](https://github.com/frappe/erpnext)                   | version-15  | Accounting, invoicing, inventory                   |
| **CRM (Summon)**   | [withsummon/crm-summon](https://github.com/withsummon/crm-summon)     | develop     | Lead/deal management, pipeline, kanban             |
| **Drive**          | [frappe/drive](https://github.com/frappe/drive)                       | main        | File storage & management                          |
| **Helpdesk**       | [frappe/helpdesk](https://github.com/frappe/helpdesk)                 | main        | Ticketing, SLA, knowledge base                     |
| **Insights**       | [frappe/insights](https://github.com/frappe/insights)                 | version-3   | Data analytics, dashboards, query builder          |
| **Lending**        | [frappe/lending](https://github.com/frappe/lending)                   | version-15  | Loan management, disbursement, repayment           |
| **Telephony**      | [frappe/telephony](https://github.com/frappe/telephony)               | develop     | Twilio/Exotel call integration                     |
| **Omnichannel Chat** | [clefincode/clefincode_chat](https://github.com/clefincode/clefincode_chat) | develop | WhatsApp, multi-channel messaging                  |

---

## FAQ

### Q: Apakah saya harus push `my-frappe-bench` ke GitHub?

**Tidak.** `my-frappe-bench` adalah environment runtime yang berisi:
- `env/` — Python virtual environment (machine-specific, file besar)
- `sites/` — Database config, password, encryption key (data sensitif!)
- `logs/` — File log (tidak perlu di-track)
- `apps/` — Semua app sudah punya repo Git masing-masing

Yang perlu kamu push hanya **`frappe-crm`** (repo ini). Orang lain bisa setup ulang bench menggunakan panduan di file ini.

---

### Q: Kalau saya push frappe-crm saja, apakah fitur Drive/Helpdesk/dll tetap ada?

**Fitur-fitur tersebut bukan bagian dari repo `frappe-crm`.** Mereka adalah app terpisah yang di-install di bench. File `apps.json` di repo ini mendokumentasikan semua app yang diperlukan, sehingga orang lain bisa menginstallnya dengan mudah.

---

### Q: Bagaimana cara update app ke versi terbaru?

```bash
cd my-frappe-bench

# Update satu app
bench update --apps frappe

# Update semua app
bench update

# Update dan migrate database
bench update --patch
```

---

### Q: Bagaimana cara menambah app baru?

```bash
cd my-frappe-bench
bench get-app <nama-app-atau-url-git>
bench --site crm.localhost install-app <nama-app>
```

Jangan lupa tambahkan juga ke `apps.json` di repo `frappe-crm` agar terdokumentasi.

---

### Q: Bagaimana cara backup site?

```bash
cd my-frappe-bench
bench --site crm.localhost backup --with-files
```

File backup tersimpan di `sites/crm.localhost/private/backups/`.

---

### Q: Bagaimana cara restore dari backup di mesin baru?

Setelah setup bench dan install semua app mengikuti panduan di atas:

```bash
bench --site crm.localhost restore \
  <path-ke-file-sql.gz> \
  --with-private-files <path-ke-private-files.tar> \
  --with-public-files <path-ke-public-files.tar>

bench --site crm.localhost migrate
```
