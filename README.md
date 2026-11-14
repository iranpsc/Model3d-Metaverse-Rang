# 🎨 Model3D-Metaverse-Rang | مخزن مهندسی و توسعه مدل‌های سه‌بعدی متاورس رنگ
### Official 3D Spatial Asset Pipeline, Modular Architecture & Open-Source Modeling Hub for the MetaRang Parallel World
**Architected & Maintained by [Paradise Supply Chain Holding (`IranPSC`)](https://github.com/iranpsc)**

[](https://metarang.com/en/about)
[](https://www.gnu.org/licenses/agpl-3.0.en.html)
[](https://github.com/iranpsc/Model3d-Metaverse-Rang)
[](https://docs.google.com/document/d/1V3WmtzFnHSwDsLzdFEuchUnKyaG5WHXqFAkYych4QGw/edit?usp=drivesdk&ouid=105432883195858560779)
[](https://github.com/iranpsc/Metaverse-Rang-World-3D-Multiverse)
[](https://github.com/orgs/iranpsc/projects/2)

[**MetaRang Portal (`metarang.com`)**](https://metarang.com/en/about) • [**3D RGB Marketplace (`3d.irpsc.com`)**](https://3d.irpsc.com) • [**3D Multiverse Client**](https://github.com/iranpsc/Metaverse-Rang-World-3D-Multiverse) • [**Organization Project Board (`projects/2`)**](https://github.com/orgs/iranpsc/projects/2) • [Browse Open 3D Tasks (Issues)](https://www.google.com/search?q=https://github.com/iranpsc/Model3d-Metaverse-Rang/issues)


> [!IMPORTANT]
> **Single Source of Truth for 3D Asset Production:** [**`Model3d-Metaverse-Rang`**](https://github.com/iranpsc/Model3d-Metaverse-Rang) is the official international open-source repository governing the design, optimization, UV tiling, 4K PBR texturing, native source archiving, and **unpacked `glTF 2.0`** delivery of all 3D spatial assets—including architectural landmarks, urban buildings, vehicles, props, and interactive components—deployed across the **[MetaRang (Metaverse Rang)](https://metarang.com/en/about)** parallel world. Every modeling request is published as a structured **GitHub Issue** tagged with its **Requester ID** (such as `bn-1000` for the **Matrix Exit Fund**), developed on dedicated feature branches, validated through **Pull Requests**, and merged into `main` for direct ingestion into the MetaRang 3D engine and [**3D RGB Marketplace (`3d.irpsc.com`)**](https://3d.irpsc.com).

## 📖 1. Executive Overview & Mission

In hyperscale virtual worlds, unoptimized 3D geometry and embedded monolithic textures prevent dynamic material hot-swapping and cause GPU memory (`VRAM`) exhaustion. As detailed in the [**MetaRang Multi-Platform Texturing & Rendering Engineering Framework**](https://docs.google.com/document/d/1V3WmtzFnHSwDsLzdFEuchUnKyaG5WHXqFAkYych4QGw/edit?usp=drivesdk&ouid=105432883195858560779), MetaRang operates on an ultra-lightweight **`<10MB` initial client bootstrap** in [**Metaverse-Rang-World-3D-Multiverse**](https://github.com/iranpsc/Metaverse-Rang-World-3D-Multiverse), where all world assets are streamed additively based on avatar proximity (`LOD`) and a **7-tier KTX2 / Basis Universal texture resolution pyramid (`64px` to `4096px`)**.

This repository transitions our 3D production pipeline from internal workgroups into a **transparent, decentralized, international GitHub workflow** under the **GNU Affero General Public License v3.0 (`AGPL-3.0`)**:
- **📋 Issue-Driven 3D Task Briefs:** Every required 3D model (mega-structures, modular buildings, urban furniture, micro-props, or environmental assets) is published as a formal [GitHub Issue](https://www.google.com/search?q=https://github.com/iranpsc/Model3d-Metaverse-Rang/issues) complete with **Requester Category & ID** (e.g., `investors/bn-1000`), concept art, orthographic reference images, video walkthroughs, and spatial dimensions.
- **🗂️ Requester-Scoped & Segregated File Hierarchy:** All assets are organized by requester category and unique ID (e.g., `investors/bn-1000/<Object-Name-In-English>/`) with segregated subdirectories for **unpacked `gltf/`**, external **`textures/`** (`4K`), editable **`source/`** files, and **`previews/`**.
- **🔄 Dynamic Texture Hot-Swapping (`Unpacked .gltf`):** Models are delivered as **unpacked `.gltf` files** (referencing external texture files rather than packed `.glb` binaries) so that replacing or updating any texture file manually inside the `textures/` folder immediately updates the 3D model's appearance without re-exporting from 3D software.
- **🌍 Verified International Portfolio for 3D Artists:** Because this repository is 100% public and linked to our central [**Organization Project Board (`github.com/orgs/iranpsc/projects/2`)**](https://github.com/orgs/iranpsc/projects/2), every merged 3D model and Pull Request is permanently recorded on the contributor's international GitHub profile as a verified production contribution to a national metaverse infrastructure.

## 🗂️ 2. Mandatory Directory Hierarchy (Organized by Requester ID)

Every 3D model in this repository **MUST** be stored under the directory of its **Requester Category** and **Unique Requester ID** (for example, **`bn-1000`** representing the **Matrix Exit Fund / صندوق خروج از ماتریکس** under `investors/`). Inside the requester ID folder, create a dedicated folder using the **English name of the object** (`PascalCase` or `kebab-case`) containing segregated subfolders for `gltf/`, `textures/`, `source/`, and `previews/`:

```text
Model3d-Metaverse-Rang/
├── investors/                                      # Requester Category: Institutional Investors & Funds
│   └── bn-1000/                                    # Unique Requester ID (e.g., bn-1000 = Matrix Exit Fund)
│       ├── Matrix-Central-Tower/                   # Object Name in English (If >100MB, split into modular folders)
│       │   ├── gltf/                               # Unpacked glTF 2.0 output (.gltf + .bin) referencing ../textures/
│       │   │   ├── Matrix-Central-Tower.gltf       # JSON scene descriptor with relative paths to ../textures/
│       │   │   └── Matrix-Central-Tower.bin        # Binary geometry buffer (strictly <= 100 MB)
│       │   ├── textures/                           # External 4K (4096x4096) Tiled PBR textures (Manual swap updates model)
│       │   │   ├── Tex_Concrete_Wall_01_BaseColor_4096.png
│       │   │   ├── Tex_Concrete_Wall_01_ORM_4096.png
│       │   │   └── Tex_Concrete_Wall_01_Normal_4096.png
│       │   ├── source/                             # Raw editable 3D software source file (strictly <= 100 MB, unpacked)
│       │   │   └── Matrix-Central-Tower.blend      # (.blend, .max, .ma, .mb, or .fbx with external texture links)
│       │   ├── previews/                           # Visual QA verification renders (.png / .webp)
│       │   │   ├── 01-beauty-render.png
│       │   │   ├── 02-wireframe-topology.png
│       │   │   └── 03-uv-checkerboard.png
│       │   └── metadata.json                       # Bounding box dimensions (L/W/H), SubMeshes, Requester ID
│       │
│       ├── Matrix-Central-Tower-Part2-Plaza/       # Modular split example when total structure exceeds 100 MB
│       │   ├── gltf/
│       │   ├── textures/
│       │   ├── source/
│       │   └── previews/
│       │
│       └── Futuristic-Street-Bench/                # Small/Medium object example under bn-1000
│           ├── gltf/
│           ├── textures/
│           ├── source/
│           └── previews/
│
├── citizens/                                       # Requester Category: Citizen VOD Orders (by Citizen ID, e.g., hm-2000001)
│   └── hm-XXXXXXX/
│       └── <Object-Name-In-English>/
│           ├── gltf/
│           ├── textures/
│           ├── source/
│           └── previews/
│
└── metarang-core/                                  # Requester Category: Core Public Infrastructure & Islands
    └── <Island-or-Department-ID>/
        └── <Object-Name-In-English>/
            ├── gltf/
            ├── textures/
            ├── source/
            └── previews/
```

## 📐 3. Mandatory 3D Modeling, Source File, UV Tiling & `glTF` Standards

> [!CAUTION]
> **Strict Compliance Required Before Pull Request Approval:** Every 3D asset submitted to this repository is ingested directly into the real-time **Unity WebGL / Windows / Android / VR** rendering pipeline and the **7-tier KTX2 backend worker**. Models that use packed `.glb` instead of unpacked `.gltf`, omit editable `source/` files, or violate the `100 MB` cap will be rejected during Pull Request review.

### A. Output Format, Source Files & Size Limits
| Parameter | Mandatory MetaRang Standard | Technical Rationale & Engine Compatibility |
| :--- | :--- | :--- |
| **Delivery Format (`gltf/`)** | **Unpacked `glTF 2.0 Separate`** (`.gltf` + `.bin` + external `textures/`) | **Do NOT use monolithic `.glb`.** Using unpacked `.gltf` with relative URI paths (`../textures/...`) ensures that replacing any texture file manually inside `textures/` immediately updates the 3D model without re-exporting. |
| **Editable Source File (`source/`)** | **Mandatory Raw Source File** (`.blend`, `.max`, `.ma`/`.mb`, or `.fbx`) | Every asset folder **MUST** include its native editable source file inside `source/`. Save source files **without packing/embedding 4K textures inside the `.blend`/`.max` file** (use relative links to `../textures/`) so the source file remains lightweight and strictly **`<= 100 MB`**. |
| **Polygon / Triangle Count** | **No Fixed Ceiling (Optimization-Driven)** | There is no rigid polygon cap; geometry detail should match the visual fidelity of the reference brief while keeping topology clean (no redundant subdivisions) and strictly respecting the **`<= 100 MB`** size ceiling. |
| **Master Texture Resolution** | **`4K (4096 × 4096 px)`** (Power-of-Two strictly enforced) | Master 4K source maps in `textures/` are automatically downsampled by the MetaRang backend worker into 7 KTX2 tiers (`4096`, `2048`, `1024`, `512`, `256`, `128`, `64`). |
| **Maximum Size Limit** | **`<= 100 MB` per model & per file** (Hard Ceiling) | Guarantees smooth GitHub LFS storage, fast asynchronous distance-based streaming (`Async Distance Loading`), and zero VRAM spikes. |
| **Over-100MB Modular Rule** | **Mandatory Modular Decomposition (Sub-Models)** | Any building, landmark, or complex exceeding `100 MB` **MUST** be split into logical modular sub-models (e.g., `Tower-Base`, `Tower-Mid`, `Tower-Crown`, `Interior-Props`) where every individual module and source file is strictly **`<= 100 MB`**. |
| **Unit Scale & Pivot** | **`1 Unit = 1.0 Meter`**, **`+Y Up`**, Pivot at **Bottom-Center (`Y = 0`)** | Ensures exact physical alignment on MetaRang GIS land parcels (`VOD`) and clean collider generation in **MetaRang Native Studio** with frozen transforms (`Scale = 1,1,1`, `Rotation = 0,0,0`). |

### B. Tiled Texturing Architecture & UV Unwrapping Standards
To achieve maximum rendering performance across thousands of concurrent buildings and props while utilizing the centralized [**MetaRang Texture Pyramid (`Wood`, `Metal`, `Concrete`, `Fabric`, `Glass`, `Stone`)**](https://docs.google.com/document/d/1V3WmtzFnHSwDsLzdFEuchUnKyaG5WHXqFAkYych4QGw/edit?usp=drivesdk&ouid=105432883195858560779):

1. **Tile-Based Texturing Workflow (Seamless Tiling & Trim Sheets):**
   - Architectural surfaces (walls, facades, roofs, pavements, structural columns, terrain) **MUST** use **seamless tileable 4K PBR textures** and **modular trim sheets** rather than unique 1:1 baked megatextures.
   - Because `.gltf` files reference external textures in `../textures/`, any artist or automated pipeline can swap a tiled 4K texture in the `textures/` folder and immediately see the updated material on the 3D model.
2. **UV Unwrapping & Texel Density Rules:**
   - **Consistent Texel Density:** Maintain uniform texel density across all contiguous modules of a building or prop so tiled 4K textures never appear stretched, warped, or inconsistently scaled across adjacent meshes.
   - **Clean UV Unwrapping:** Ensure zero unintended distortion, logical seam placement along hard edges, and proper island orientation aligned with material grain/direction.
3. **4K PBR Metallic-Roughness Material Channels:**
   - **BaseColor / Albedo (`4096×4096`, sRGB):** Clean diffuse reflectance without baked directional shadows (converted downstream via `KTX2 ETC1S`).
   - **ORM Packed Map (`4096×4096`, Linear):** Channel-packed texture storing **Ambient Occlusion (`R`)**, **Roughness (`G`)**, and **Metallic (`B`)** in a single image (converted downstream via `KTX2 UASTC`).
   - **Normal Map (`4096×4096`, Linear, OpenGL `+Y`):** Tangent-space normal map free of shading seams (converted downstream via `KTX2 UASTC`).

## 🔄 4. End-to-End Contribution Workflow (With `Git LFS` Support)

All 3D modeling tasks follow a strict 5-stage Git workflow integrated with our [**Organization Project Board (`github.com/orgs/iranpsc/projects/2`)**](https://github.com/orgs/iranpsc/projects/2):

### Step 1: Select a 3D Modeling Task in GitHub Issues
1. Open the [Issues Tab (github.com/iranpsc/Model3d-Metaverse-Rang/issues)](https://www.google.com/search?q=https://github.com/iranpsc/Model3d-Metaverse-Rang/issues).
2. Each issue specifies:
   - **Requester Category & ID:** e.g., `investors/bn-1000` (Matrix Exit Fund).
   - **Object English Name:** e.g., `Matrix-Central-Tower`.
   - **Visual Brief:** Reference images, architectural diagrams, and explanatory video walkthroughs.
3. Comment on the issue to claim the task before starting work.

### Step 2: Clone, Configure `Git LFS` & Create a Dedicated Branch
Because 3D geometry buffers (`.bin`), native source files (`.blend`/`.max`/`.fbx`), and `4K` textures can range between `50 MB` and `100 MB`, **always enable `Git LFS` (Large File Storage)** so GitHub accepts your push smoothly without file-size warnings:

```bash
# 1. Clone the repository
git clone https://github.com/iranpsc/Model3d-Metaverse-Rang.git
cd Model3d-Metaverse-Rang

# 2. Initialize Git LFS for 3D source, binary, and 4K texture files (up to 100 MB)
git lfs install
git lfs track "*.bin" "*.blend" "*.fbx" "*.max" "*.ma" "*.mb" "*.png" "*.jpg" "*.TGA" "*.ktx2"
git add .gitattributes

# 3. Create your dedicated feature branch named after the Issue and Requester ID
git checkout -b feat/issue-<ISSUE_NUMBER>-<requester-id>-<object-name>
# Example: git checkout -b feat/issue-12-bn-1000-matrix-central-tower
```

### Step 3: Export Unpacked `.gltf`, Save Raw Source & Organize Folders
1. In Blender / 3ds Max / Maya, export the model using **`glTF 2.0 Separate (.gltf + .bin + textures)`** (do **not** export as packed `.glb`).
2. Verify that the `.gltf` JSON file references textures using relative paths (`../textures/<TextureName>.png`) so changing a file in `textures/` dynamically updates the 3D model.
3. Save your clean editable source file (`.blend`, `.max`, etc.) inside `source/` **with external texture paths (unpacked)** so the source file size remains well below `100 MB`.
4. Place all files under `<category>/<requester-id>/<Object-Name-In-English>/` (`gltf/`, `textures/`, `source/`, `previews/`).

### Step 4: Push Branch & Open a Standardized Pull Request (PR)
```bash
git add .
git commit -m "feat(3d): add <Object-Name> under <requester-id> (Closes #<ISSUE_NUMBER>)"
git push origin feat/issue-<ISSUE_NUMBER>-<requester-id>-<object-name>
```
Open a Pull Request on GitHub targeting the `main` branch and notify the review team.

### Step 5: Technical Review & Merge to `main`
The **MetaRang 3D Review Team** inspects the model on your branch (verifying the unpacked `.gltf` structure, manual texture replacement responsiveness, `source/` file integrity, UV tiling, and `<= 100 MB` compliance) and merges the approved Pull Request into `main`.

## ✅ 5. Pull Request (PR) Template & Mandatory QA Checklist

> [!NOTE]
> Copy and complete the template below in your Pull Request description when submitting a new 3D model:

```markdown
## 🎨 3D Asset Submission — Linked Issue: Closes #<ISSUE_NUMBER>

### 🗂️ Directory & Requester Metadata
- **Requester Category & ID:** `e.g., investors/bn-1000`
- **Object English Folder Name:** `e.g., Matrix-Central-Tower`
- **Target Directory Path:** `<category>/<requester-id>/<Object-Name-In-English>/`
- **Modular Split Status:** `[ ] Single Model (<= 100 MB)` | `[ ] Split into __ Modular Sub-Models (Each <= 100 MB)`

### 📊 Technical Specifications & Package Metrics
- **Bounding Box Dimensions (Meters):** `Length: __m × Width: __m × Height: __m`
- **Geometry Counts:** `Vertices: ____` | `Triangles/Polygons: ____` | `SubMeshes: ____`
- **File Sizes (Must each be <= 100 MB):**
  - `gltf/` (`.gltf` + `.bin`): `____ MB`
  - `textures/` (`4K` Tiled PBR Maps): `____ MB`
  - `source/` (Raw `.blend` / `.max` / `.ma` / `.fbx`): `____ MB`

### 🖼️ Required Visual Verification Screenshots (Attach Below)
1. **Textured Beauty Render (Front & Perspective View)**
2. **Wireframe / Clay Topology View (Showing clean edge flow)**
3. **UV Layout & Checkerboard Tiling View (Showing uniform texel density)**

### 🛡️ Mandatory 3D Quality Gate Checklist
- [ ] **Requester Directory Structure:** Placed accurately under `<category>/<requester-id>/<Object-Name-In-English>/` with segregated `gltf/`, `textures/`, `source/`, and `previews/` folders.
- [ ] **Unpacked `.gltf` Format (Dynamic Texture Swap Verified):** Exported as separate `.gltf` + `.bin` referencing external `../textures/` (NOT a packed `.glb`), and tested to ensure replacing a texture file manually updates the 3D model.
- [ ] **Editable Raw Source Included (`source/`):** Native source file (`.blend`/`.max`/`.ma`/`.fbx`) is included in `source/` without embedded megatextures and is strictly `<= 100 MB`.
- [ ] **Size Cap (`<= 100 MB`) & Git LFS:** Total package and individual files are strictly `<= 100 MB` (or split into modular sub-models), and binary/source files are tracked via `Git LFS`.
- [ ] **4K Tiled PBR Textures & Proper UVs:** All master textures are `4096 × 4096 px`, tile-based (`Seamless Tiling / Trim Sheets`), with clean UV unwrapping and uniform texel density.
- [ ] **Metric Scale, Pivot & Clean Topology:** Modeled at `1 Unit = 1 Meter`, pivot at bottom-center (`Y = 0`), frozen transforms (`Scale = 1,1,1`), clean topology, and logically separated sub-meshes for **MetaRang Native Studio** colliders.
- [ ] **License Agreement:** Submitted under the **GNU Affero General Public License v3.0 (`AGPL-3.0`)**.
```


## 🇮🇷 ۶. چکیده اجرایی و راهنمای جامع مشارکت در مخزن مدل‌سازی سه‌بعدی متاورس رنگ (Persian Executive Summary)

مخزن رسمی **[`Model3d-Metaverse-Rang`](https://github.com/iranpsc/Model3d-Metaverse-Rang)** در بستر **[ارگانیزیشن گیت‌هاب هلدینگ زنجیره تأمین بهشت (`iranpsc`)](https://github.com/iranpsc)**، مرکز تخصصی و بین‌المللی تعریف تسک‌ها، طراحی، بهینه‌سازی و انتشار تمامی **مدل‌های سه‌بعدی پروژه متاورس رنگ | متارنگ ([metarang.com](https://metarang.com/en/about))** است. تمامی مدل‌های تولیدشده در این مخزن پس از تایید فنی و ادغام روی شاخه `main`، مستقیماً در جهان سه‌بعدی متارنگ ([Metaverse-Rang-World-3D-Multiverse](https://github.com/iranpsc/Metaverse-Rang-World-3D-Multiverse)) و بازارچه **[سه‌بعدی متا (`3d.irpsc.com`)](https://3d.irpsc.com)** مورد استفاده قرار می‌گیرند.

### 🎯 چرخه کاری جدید (از ثبت Issue تا Pull Request و رزومه‌سازی بین‌المللی)
کلیه سفارش‌ها و تسک‌های ساخت مدل‌های سه‌بعدی متارنگ (شامل ساختمان‌ها، سازه‌های کلان، اجسام کوچک و بزرگ) به همراه **شناسه درخواست‌دهنده، تصاویر مرجع و ویدیوی توضیحات** در بخش **[Issues این ریپازیتوری](https://www.google.com/search?q=https://github.com/iranpsc/Model3d-Metaverse-Rang/issues)** منتشر می‌شوند:
1. **انتخاب تسک و ایجاد شاخه (`Branch`):** توسعه‌دهندگان و طراحان سه‌بعدی در سراسر جهان پس از بررسی Issue، تسک را انتخاب کرده و با فعال‌سازی **`Git LFS`**، اقدامات طراحی و بهینه‌سازی را روی یک شاخه (`Branch`) مجزا انجام می‌دهند.
2. **ثبت `Pull Request` توسط طراح و بررسی فنی:** پس از اتمام طراحی، طراح شخصاً با رعایت استانداردهای مخزن اقدام به ثبت **Pull Request** می‌کند تا مدل تولیدشده توسط تیم فنی بررسی و در صورت تایید روی شاخه اصلی (`main`) پوش و ادغام شود.
3. **رزومه‌سازی معتبر جهانی تحت لایسنس `AGPL-3.0`:** به دلیل عمومی بودن مخزن و اتصال به **[برد رسمی پروژه متارنگ (`github.com/orgs/iranpsc/projects/2`)](https://github.com/orgs/iranpsc/projects/2)**، تمامی کامیت‌ها و Pull Requestهای تاییدشده به عنوان سابقه رسمی مشارکت در یک کلان‌پروژه بین‌المللی در پروفایل گیت‌هاب طراح ثبت می‌گردد.

### 🗂️ قانون ساختار دایرکتوری‌ها بر اساس شناسه درخواست‌دهنده (مثال: `bn-1000`)
تمامی دایرکتوری‌ها در این مخزن بر اساس **گروه و شناسه یکتای درخواست‌دهنده** ساختاردهی می‌شوند. به عنوان مثال، برای سفارش‌های ثبت‌شده توسط **«صندوق خروج از ماتریکس» با شناسه `bn-1000`**:
- مدل‌ها در دایرکتوری سرمایه‌گذاران (`investors/`) و زیرپوشه اختصاصی شناسه درخواست‌دهنده یعنی **`investors/bn-1000/`** قرار می‌گیرند.
- در داخل پوشه `bn-1000/`، برای هر مدل یک پوشه با **نام انگلیسی آبجکت** (مثلاً `investors/bn-1000/Matrix-Central-Tower/`) ایجاد می‌شود.
- در داخل پوشه هر آبجکت، فایل‌ها به صورت کاملاً تفکیک‌شده در ۴ زیرپوشه مجزا قرار می‌گیرند:
  1. **`gltf/`:** حاوی خروجی باز **`.gltf` و `.bin`** (متصل به پوشه `../textures/`).
  2. **`textures/`:** حاوی تکسچرهای مادر **`4K (4096×4096)`** به صورت تایل‌بندی‌شده.
  3. **`source/`:** حاوی **فایل خام قابل ویرایش نرم‌افزار** (مانند `.blend`، `.max`، `.ma` یا `.fbx` بدون تکسچرهای Embedشده تا حجم آن زیر ۱۰۰ مگابایت بماند).
  4. **`previews/`:** حاوی تصاویر رندر نهایی، شبکه Wireframe و چیدمان UV برای بررسی سریع در Pull Request.

### 📏 استانداردهای فنی الزامی برای تایید مدل‌های سه‌بعدی در متارنگ
- **۱. تحویل به صورت فایل باز `.gltf` (تغییر پویا و دستی تکسچرها):** خروجی مدل حتماً باید به صورت **فایل باز `.gltf` به همراه پوشه تکسچرهای جداگانه** باشد (نه فایل بسته `.glb`)، به‌گونه‌ای که اگر هر یک از فایل‌های تکسچر در پوشه `textures/` به صورت دستی جایگزین یا ویرایش شود، ظاهر مدل سه‌بعدی بلافاصله بدون نیاز به خروجی گرفتن مجدد تغییر کند.
- **۲. تحویل الزامی فایل خام (`source/`) با رعایت سقف حجم:** قرار دادن فایل خام طراحی در پوشه `source/` الزامی است، اما فایل خام نباید تکسچرهای حجیم را در دل خود Pack کرده باشد و حجم آن نباید از سقف مجاز (`100 MB`) فراتر رود.
- **۳. تکسچرهای `4K`، طراحی تایل‌بندی (`Tiling`) و `UV` مهندسی‌شده:** تمامی تکسچرها باید با کیفیت **`4K (4096×4096)`**، بر پایه استاندارد تایل‌بندی (**Seamless Tiling & Trim Sheets**) و با **UV مناسب و تراکم پیکسلی یکنواخت** تولید شوند تا در پایپ‌لاین [معماری ۷ سطحی KTX2 متارنگ](https://docs.google.com/document/d/1V3WmtzFnHSwDsLzdFEuchUnKyaG5WHXqFAkYych4QGw/edit?usp=drivesdk&ouid=105432883195858560779) (از ۶۴ تا ۴۰۹۶ پیکسل) بهترین عملکرد را داشته باشند.
- **۴. سقف حجم `100 MB` و تفکیک ماژولار مدل‌های بزرگ (بدون محدودیت خشک پلی‌گان):** محدودیت ثابتی برای تعداد پلی‌گان‌ها تعیین نشده است، اما توپولوژی باید کاملاً بهینه باشد و **حجم کل مدل یا هیچ فایل خامی نباید از ۱۰۰ مگابایت (`100 MB`) بیشتر باشد**. اگر سازه‌ای بیش از ۱۰۰ مگابایت حجم دارد، باید به چند مدل کوچک‌تر و ماژولار تفکیک شود.


## 🔗 7. Ecosystem Links & Connected Repositories

- 🌍 **MetaRang Official Portal:** [https://metarang.com/en/about](https://metarang.com/en/about)
- 📊 **MetaRang GitHub Project Board (`SSOT`):** [https://github.com/orgs/iranpsc/projects/2](https://github.com/orgs/iranpsc/projects/2)
- 🎨 **3D Modeling Repository (`Model3d-Metaverse-Rang`):** [https://github.com/iranpsc/Model3d-Metaverse-Rang](https://github.com/iranpsc/Model3d-Metaverse-Rang)
- 🎮 **MetaRang 3D Multiverse Client (`Unity`):** [https://github.com/iranpsc/Metaverse-Rang-World-3D-Multiverse](https://github.com/iranpsc/Metaverse-Rang-World-3D-Multiverse)
- 🖥️ **MetaRang 3D Spatial Server (`Node.js / VME2`):** [https://github.com/iranpsc/Metaverse-Rang-World-3D-Multiverse-Server](https://github.com/iranpsc/Metaverse-Rang-World-3D-Multiverse-Server)
- 🛒 **3D RGB Asset Marketplace (`3d.irpsc.com`):** [https://github.com/iranpsc/3DMeta-Shop-Object-3D](https://github.com/iranpsc/3DMeta-Shop-Object-3D)


**Licensed under the [GNU Affero General Public License v3.0 (`AGPL-3.0`)](https://www.gnu.org/licenses/agpl-3.0.en.html) • © [Paradise Supply Chain Holding (`IranPSC`)](https://github.com/iranpsc)**

