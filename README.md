<div align="center">

# 🌐 Model3d-Metaverse-Rang
**Official Open-Source 3D Spatial Asset Pipeline & Collaborative Modeling Repository for the MetaRang Parallel World**

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![3D Standard: glTF 2.0](https://img.shields.io/badge/3D_Standard-glTF_2.0-green.svg)](https://www.khronos.org/gltf/)
[![Texture Pipeline: 4K to KTX2](https://img.shields.io/badge/Textures-4K_PNG_%E2%86%92_KTX2-orange.svg)](#)
[![Git LFS: Required](https://img.shields.io/badge/Git_LFS-Required-critical.svg)](https://git-lfs.com/)

[🇬🇧 English Documentation](#-english-documentation) | [🇮🇷 مستندات فارسی](#-مستندات-فارسی)

</div>

---

# 🇬🇧 English Documentation

## 📖 Overview
Welcome to **Model3d-Metaverse-Rang**, the official repository for submitting, validating, and maintaining 3D spatial assets, architectural landmarks, props, and environmental modules for the **MetaRang (Metaverse Rang)** ecosystem.

To guarantee real-time WebGPU/WebGL performance across mobile, desktop, and VR platforms while preserving high visual fidelity, all 3D contributors must strictly adhere to the directory structures, modeling budgets, texture specifications, and package optimization rules defined in this document.

---

## 📁 Repository & Asset Directory Structure

Every 3D model or modular asset must be placed inside its respective category folder and follow this exact directory layout:

```text
categories/
└── <category_name>/               # e.g., landmarks, architecture, props, vehicles, foliage
    └── <model_name>/              # e.g., lighthouse, city_hall (lowercase_snake_case)
        ├── source/                # Clean native source file (.blend, .max, .ma) - NO backups (.blend1)
        ├── textures/              # Raw 4K PBR textures (.png) - Single source of truth
        ├── gltf/                  # Exported glTF Separate (.gltf + .bin) referencing ../textures/
        ├── preview/               # Visual inspection renders (WebP/PNG, total < 10 MB)
        └── metadata.json          # Asset manifest, scale, LOD info, and author metadata
```

> ⚠️ **CRITICAL RULE:** Do **NOT** duplicate textures across `source/`, `textures/`, and `gltf/`. All textures must live exclusively in `textures/`.

---

## 🎨 Modeling & Technical Standards

### 1. Coordinate System, Units & Scale
* **Units:** Metric (`1 unit = 1 meter`).
* **Up Axis:** `+Y` Up (glTF 2.0 standard — Blender exports this automatically when `+Y Up` is checked).
* **Forward Axis:** `-Z` Forward (`+Z` in glTF space).
* **Transforms:** All objects must have their transforms applied (`Location: 0,0,0`, `Rotation: 0,0,0`, `Scale: 1,1,1`) before export.
* **Pivot Point:** Set at the bottom-center (`Z = 0`) of the model's bounding box for grounded assets.

### 2. Geometry & Topology
* **Quads/Tris:** Clean topology ready for real-time triangulation. Avoid N-gons, non-manifold geometry, zero-area faces, and overlapping vertices.
* **Modular Splitting (100 MB Rule):** Any asset or architectural complex whose single file or logical module exceeds **100 MB** must be split into logical sub-modules (e.g., `base`, `tower`, `interior_props`).
* **UV Mapping:**
  * `UVMap_0` (Channel 0): Non-overlapping UVs (or deliberate modular trim/tile UVs) within `0–1` space for PBR textures.
  * `UVMap_1` (Channel 1 - Optional): Non-overlapping lightmap/AO UVs with proper padding.

### 3. PBR Texture Pipeline (4K Source $\rightarrow$ 7-Level KTX2 Pyramid)
* **Submission Format:** Submit uncompressed/lossless **4K (`4096×4096`) PNG** textures in the `textures/` directory.
* **Server-Side Processing:** Our automated CI/CD pipeline converts your 4K PNGs into a **7-level mipmapped KTX2 (Basis Universal / UASTC & ETC1S)** texture pyramid for adaptive streaming in the browser.
* **Naming Convention:**
  * `<model_name>_<material>_BaseColor.png` (`sRGB`)
  * `<model_name>_<material>_Normal.png` (`Linear`, OpenGL `+Y` tangent space)
  * `<model_name>_<material>_ORM.png` (`Linear`, packed channels: **R** = Ambient Occlusion, **G** = Roughness, **B** = Metallic)
  * `<model_name>_<material>_Emissive.png` (`sRGB`, optional)

---

## 📦 Package Size Optimization & Blender Export Guide

To prevent repository bloat, duplicate textures, and GitHub push rejections, strictly follow these rules before committing your package:

### 1. Clean Up Source Folder (`source/`)
* **No Backup Files:** Never commit Blender backup files (`*.blend1`, `*.blend2`), Substance Painter autosaves, or temporary bake caches.
* **Unpack Resources:** Do not pack textures inside the `.blend` file. In Blender, go to `File > External Data > Unpack Resources` (and ensure `Automatically Pack Resources` is unchecked) so your `.blend` file contains only geometry and scene data.

### 2. Avoid Texture Duplication in `gltf/` (`glTF Separate`)
When exporting a model with 250+ MB of 4K textures, using `glTF Binary (.glb)` or `Embedded` copies all textures into the `gltf/` folder, doubling your package size. Instead:
* **Centralized Textures:** Place all raw 4K PBR textures (`PNG`) strictly inside the `textures/` folder. Do not leave copies inside `source/` or `gltf/`.
* **Blender glTF 2.0 Export Settings:**
  * **Format:** Select `glTF Separate (.gltf + .bin + textures)`.
  * **Texture Directory:** Set path to `../textures/` (or delete any duplicate exported textures inside `gltf/` and verify that the `.gltf` JSON file references `../textures/<texture_name>.png`).
  * **Result:** The `gltf/` directory will only contain lightweight `.gltf` and `.bin` geometry data (typically `5 MB – 30 MB`).

### 3. Optimize Preview Renders (`preview/`)
* Keep the total size of the `preview/` folder **under 10 MB**.
* Provide 3 to 5 clear renders (Front, Perspective, Wireframe, UV/Material) in `1920×1080` resolution using compressed `PNG` or `WebP`.

### 4. Understanding the 100 MB Limit & Multi-Stage Commits
* The **100 MB limit** applies to **single files** (without Git LFS) and **individual Git pushes** to prevent connection timeouts and pipeline bottlenecks.
* If your cleaned total package (e.g., `50 MB` `.blend` + `260 MB` 4K `textures` + `15 MB` `gltf/preview`) exceeds 100 MB:
  1. Ensure **Git LFS** is initialized (`git lfs install`).
  2. Split your upload into **logical staged commits** within your feature branch before opening a single Pull Request:
     * **Commit & Push 1:** `source/` and `preview/` folders.
     * **Commit & Push 2:** `textures/` (split into 2 commits if textures exceed 150 MB).
     * **Commit & Push 3:** `gltf/` and `metadata.json`.

---

## 📄 Metadata Specification (`metadata.json`)

Every asset folder must include a `metadata.json` file at its root:

```json
{
  "asset_id": "lighthouse_01",
  "name": "Coastal Lighthouse",
  "category": "landmarks",
  "author": "your_github_username",
  "version": "1.0.0",
  "license": "AGPL-3.0",
  "units": "meters",
  "dimensions": {
    "width": 14.5,
    "height": 42.0,
    "depth": 14.5
  },
  "geometry": {
    "triangles": 48500,
    "vertices": 26120,
    "materials_count": 3
  },
  "textures": {
    "resolution": "4096x4096",
    "format": "PNG",
    "pbr_workflow": "Metallic-Roughness (ORM)"
  },
  "entry_gltf": "gltf/lighthouse.gltf"
}
```

---

## 🚀 Submission Workflow & Git LFS

1. **Install Git LFS (Mandatory):**
   ```bash
   git lfs install
   ```
2. **Fork & Clone the Repository:**
   ```bash
   git clone https://github.com/<your-username>/Model3d-Metaverse-Rang.git
   cd Model3d-Metaverse-Rang
   ```
3. **Create a Feature Branch:**
   ```bash
   git checkout -b feat/add-lighthouse-model
   ```
4. **Verify LFS Tracking Before Committing:**
   Run `git lfs status` after staging (`git add`) to confirm `.blend`, `.bin`, `.glb`, and `.png` files are marked as `(LFS: ...)` and no `.blend1` files are included.
5. **Commit & Push in Stages (under 100 MB per push):**
   ```bash
   git add categories/landmarks/lighthouse/source categories/landmarks/lighthouse/preview
   git commit -m "feat(lighthouse): add clean blender source and optimized previews"
   git push origin feat/add-lighthouse-model

   git add categories/landmarks/lighthouse/textures
   git commit -m "feat(lighthouse): add 4K PBR textures"
   git push origin feat/add-lighthouse-model

   git add categories/landmarks/lighthouse/gltf categories/landmarks/lighthouse/metadata.json
   git commit -m "feat(lighthouse): add separate glTF 2.0 geometry and metadata"
   git push origin feat/add-lighthouse-model
   ```
6. **Open a Pull Request** against the `main` branch and fill out the PR checklist.

---
---

<div dir="rtl">

# 🇮🇷 مستندات فارسی

## 📖 معرفی ریپازیتوری
به ریپازیتوری رسمی **Model3d-Metaverse-Rang** خوش آمدید. این مخزن، خط لوله (Pipeline) متن‌باز برای ارسال، اعتبارسنجی و نگهداری مدل‌های سه‌بعدی، بناهای شاخص، المان‌های شهری و ماژول‌های محیطی در دنیای موازی **متاورس رنگ (MetaRang)** است.

به منظور تضمین اجرای روان و بلادرنگ (Real-time) در بستر وب (WebGPU / WebGL) روی موبایل، دسکتاپ و هدست‌های واقعیت مجازی در کنار حفظ بالاترین کیفیت بصری، تمامی طراحان و مدل‌سازان سه‌بعدی موظف به رعایت دقیق ساختار پوشه‌ها، استانداردهای فنی، فرمت تکسچرها و قوانین بهینه‌سازی حجم در این مستند هستند.

---

## 📁 ساختار پوشه‌بندی مدل‌ها

هر مدل یا پکیج سه‌بعدی باید در دسته‌بندی مرتبط قرار گرفته و دقیقاً دارای ساختار پوشه‌بندی زیر باشد:

```text
categories/
└── <category_name>/               # دسته‌بندی (مثلاً landmarks, architecture, props, vehicles)
    └── <model_name>/              # نام مدل با حروف کوچک انگلیسی (مثلاً lighthouse)
        ├── source/                # فایل سورس اصلی (.blend, .max) - بدون فایل بکاپ (.blend1)
        ├── textures/              # تکسچرهای خام 4K با فرمت PNG (تنها محل قرارگیری تکسچر)
        ├── gltf/                  # خروجی glTF Separate (.gltf + .bin) لینک شده به ../textures/
        ├── preview/               # رندرهای پیش‌نمایش مدل (فرمت WebP یا PNG فشرده، مجموعاً زیر ۱۰ مگابایت)
        └── metadata.json          # فایل شناسنامه، ابعاد، تعداد پولیگون و مشخصات مدل
```

> ⚠️ **قانون بسیار مهم:** از کپی کردن و تکرار فایل‌های تکسچر در پوشه‌های `source/` و `gltf/` خودداری کنید. تمامی تکسچرها باید **فقط یک بار** و در پوشه `textures/` قرار بگیرند.

---

## 🎨 استانداردهای فنی و مدل‌سازی

### ۱. سیستم مختصات، مقیاس و واحدها
* **واحد اندازه‌گیری:** متریک (`1 Unit = 1 Meter`).
* **محور بالا (Up Axis):** محور `+Y` در خروجی glTF 2.0 (در بلندر هنگام خروجی گزینه `+Y Up` به صورت پیش‌فرض فعال است).
* **اعمال ترنسفورم‌ها (Apply Transforms):** پیش از خروجی گرفتن، تمامی مقادیر جابجایی، چرخش و مقیاس باید ریست و اعمال شوند (`Ctrl + A > All Transforms` در بلندر: `Location: 0,0,0`, `Rotation: 0,0,0`, `Scale: 1,1,1`).
* **نقطه ثقل (Pivot / Origin):** برای مدل‌های محیطی و ساختمانی، نقطه Origin باید در مرکزِ پایین‌ترین سطح مدل (`Z = 0`) قرار گیرد.

### ۲. هندسه (Geometry) و توپولوژی
* **توپولوژی تمیز:** مش‌ها باید فاقد وجوه بیش از ۴ ضلعی (N-gons)، لبه‌های باز ناخواسته (Non-manifold)، وجوه با مساحت صفر و نقاط تکراری (Overlapping Vertices) باشند.
* **قانون جداسازی ماژولار (سقف ۱۰۰ مگابایت):** هر مدل یا مجموعه ساختمانی که حجم فایل واحد یا بخش منطقی آن بیش از **۱۰۰ مگابایت** باشد، باید به زیرماژول‌های منطقی کوچک‌تر تقسیم شود.
* **یووی مپینگ (UV Mapping):**
  * کانال اول (`UVMap_0`): بدون همپوشانی (یا منطبق بر استاندارد Trim Sheet/Tiling) در بازه `0` تا `1`.
  * کانال دوم (`UVMap_1` - اختیاری): مخصوص Lightmap / Ambient Occlusion بدون هیچ‌گونه همپوشانی.

### ۳. خط لوله تکسچرهای PBR (تبدیل 4K PNG به هرم ۷ سطحی KTX2)
* **فرمت تحویل:** تکسچرها باید با رزولوشن **4K (`4096×4096`)** و فرمت بدون افت کیفیت **PNG** در پوشه `textures/` تحویل داده شوند.
* **پردازش سمت سرور:** خط لوله خودکار سرور، تکسچرهای 4K شما را به یک هرم ۷ سطحی از فرمت فشرده **KTX2** تبدیل می‌کند تا در مرورگر بر اساس فاصله دوربین به صورت هوشمند بارگذاری شوند.
* **استاندارد نام‌گذاری تکسچرها:**
  * `<model_name>_<material>_BaseColor.png` (فضای رنگی `sRGB`)
  * `<model_name>_<material>_Normal.png` (فضای `Linear`، استاندارد OpenGL `+Y`)
  * `<model_name>_<material>_ORM.png` (فضای `Linear`، ترکیب کانال‌ها: کانال **R** = Ambient Occlusion، کانال **G** = Roughness، کانال **B** = Metallic)
  * `<model_name>_<material>_Emissive.png` (فضای رنگی `sRGB` - در صورت نیاز)

---

## 📦 راهنمای بهینه‌سازی حجم پکیج و خروجی Blender به glTF

برای جلوگیری از افزایش کاذب حجم ریپازیتوری (مثلاً رسیدن یک پکیج به بیش از ۱ گیگابایت)، تکرار تکسچرها و خطای Push در گیت‌هاب، رعایت ۴ مرحله زیر پیش از ثبت Pull Request الزامی است:

### ۱. پاکسازی پوشه سورس (`source/`)
* **حذف فایل‌های پشتیبان:** به هیچ عنوان فایل‌های بکاپ بلندر (`*.blend1`, `*.blend2`) و فایل‌های موقت را در پوشه `source` قرار ندهید (این فایل‌ها صدها مگابایت حجم اضافه ایجاد می‌کنند).
* **عدم Pack کردن تکسچرها در فایل Blend:** تکسچرها نباید داخل فایل `.blend` فشرده (Pack) شوند. در بلندر از مسیر `File > External Data > Unpack Resources` مطمئن شوید که تکسچرها خارج شده‌اند و فایل `.blend` صرفاً حاوی دیتای مش و صحنه است.

### ۲. جلوگیری از تکرار تکسچرها در خروجی `gltf/`
وقتی حجم تکسچرهای 4K شما حدود ۲۵۰ مگابایت باشد، استفاده از خروجی `glTF Binary (.glb)` یا کپی کردن تکسچرها در پوشه `gltf` باعث می‌شود ۲۵۰ مگابایت در پوشه `textures` و ۲۵۰ تا ۴۵۰ مگابایت دیگر در پوشه `gltf` تکرار شود. برای حل این مشکل:
* **تجمیع تکسچرها:** تمامی تکسچرهای خام 4K باید **فقط و فقط** در پوشه `textures/` قرار بگیرند و هیچ فایلی از تکسچر در `source/` یا `gltf/` باقی نماند.
* **تنظیمات خروجی در Blender:**
  * در پنجره Export glTF 2.0، گزینه **Format** را روی **glTF Separate (`.gltf` + `.bin` + textures)** قرار دهید.
  * مسیر تکسچرها را به `../textures/` تنظیم کنید (یا پس از خروجی گرفتن، تکسچرهای کپی‌شده در پوشه `gltf/` را حذف کرده و مطمئن شوید در فایل متنی `.gltf` مسیر تصاویر به `../textures/<texture_name>.png` اشاره می‌کند).
  * با این روش، پوشه `gltf/` فقط شامل فایل‌های `.gltf` و `.bin` (دیتای خالص هندسی مش) خواهد بود و حجم آن از صدها مگابایت به **۵ تا ۳۰ مگابایت** کاهش می‌یابد.

### ۳. بهینه‌سازی پوشه پیش‌نمایش (`preview/`)
* مجموع حجم کل تصاویر پوشه `preview/` باید **کمتر از ۱۰ مگابایت** باشد.
* ۳ تا ۵ رندر واضح (نمای کلی، زاویه دید پرسپکتیو، نمای Wireframe و متریال) با رزولوشن `1920×1080` و فرمت فشرده `PNG` یا `WebP` قرار دهید.

### ۴. مدیریت قانون ۱۰۰ مگابایت در ارسال (Multi-Commit Push)
* محدودیت **۱۰۰ مگابایت** مربوط به سقف حجم هر **تک‌فایل** (بدون LFS) و سقف پایداری هر **Commit/Push** در ارتباط با سرور است.
* پس از انجام پاکسازی‌های مرحله ۱ تا ۳، اگر مجموع کل پکیج شما (مثلاً ۵۰ مگابایت فایل `.blend` + ۲۶۰ مگابایت تکسچر 4K + ۱۰ مگابایت `gltf` و `preview`) بیش از ۱۰۰ مگابایت است:
  1. ابتدا از فعال بودن `git lfs install` روی سیستم خود مطمئن شوید.
  2. فایل‌های خود را در **چند کامیت و پوش مجزا (زیر ۱۰۰ تا ۱۵۰ مگابایت در هر مرحله)** روی برنچ خود ارسال کرده و در نهایت **یک Pull Request واحد** ثبت کنید:
     * **کامیت و پوش اول:** پوشه‌های `source/` و `preview/`.
     * **کامیت و پوش دوم:** پوشه `textures/` (در صورت سنگین بودن، در ۲ کامیت مجزا).
     * **کامیت و پوش سوم:** پوشه `gltf/` و فایل `metadata.json`.

---

## ✅ چک‌لیست نهایی پیش از ثبت Pull Request

- [ ] فایل‌های پشتیبان (`*.blend1`, `*.blend2`, `*.bak`) به طور کامل حذف شده‌اند.
- [ ] تکسچرها از داخل فایل `.blend` خارج (Unpack) شده‌اند.
- [ ] تمامی تکسچرهای 4K PNG فقط در پوشه `textures/` قرار دارند و در `source/` یا `gltf/` تکرار نشده‌اند.
- [ ] خروجی `gltf/` به صورت `glTF Separate` گرفته شده و به `../textures/` لینک است.
- [ ] مجموع حجم پوشه `preview/` کمتر از ۱۰ مگابایت است.
- [ ] فایل `metadata.json` به درستی تکمیل شده است.
- [ ] تمامی فایل‌های باینری از طریق **Git LFS** ردیابی شده‌اند (`git lfs status`).

---

## 📜 لایسنس و حقوق مالکیت
تمامی کدها، ساختارها و دارایی‌های این ریپازیتوری تحت لایسنس **GNU Affero General Public License v3.0 (AGPL-3.0)** متعلق به هلدینگ زنجیره تأمین بهشت (**IranPSC**) و اکوسیستم **متاورس رنگ (MetaRang)** منتشر می‌شوند.

</div>
