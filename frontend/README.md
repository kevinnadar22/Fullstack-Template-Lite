# Frontend Documentation

This directory contains the Next.js 16 (App Router) frontend, styled with TailwindCSS and Shadcn/ui.

## 📂 Project Structure

```
frontend/
├── src/
│   ├── app/            # App Router: Pages & Layouts (next.js convention)
│   ├── components/     # Reusable UI components
│   │   ├── ui/         # Shadcn (atomic) components
│   │   └──             # Composition/Business components
│   ├── lib/            # Utilities (cn, auth helpers)
│   ├── services/       # API Clients (Fetch / Axios wrappers)
│   ├── types/          # TypeScript Interfaces & Types
│   └── schemas/        # Zod Validation Schemas (Form validation)
├── public/             # Static Assets (Images, Icons)
├── next.config.mjs     # Next.js Configuration
└── tailwind.config.ts  # Tailwind CSS Config
```

## 🚀 Key Concepts

- **Type-Safety:** Enforce TypeScript everywhere. Use interfaces (`types/`) for props and API responses.
- **Components:**
  - `ui/`: Bare-bones, reusable (atoms).
  - Outside `ui/`: Composed components (molecules/organisms).
- **App Router:** Pages are defined by file-system routing.
  - `src/app/page.tsx` → Home `/`
  - `src/app/dashboard/page.tsx` → Dashboard `/dashboard`
- **Services:** Encapsulate API calls in `services/`.
  - Don't call `fetch` directly in components; create a function like `getUser()` there.
- **Server Components (RSC):** Default in Next.js 13+. Use client components `'use client'` explicitly for interactivity.

## 🛠️ How to Add a New Feature

Example: Adding a Product Listing Page

1.  **Define Types:**
    Create/Update `src/types/product.ts` defining `Product`.

2.  **Create Service Function:**
    Create/Update `src/services/product.ts` with `getProducts()`.
    - This function fetches from the backend API.

3.  **Create UI Component:**
    Create `src/components/ProductCard.tsx` (reusable item).
    - Props: `product: Product`.

4.  **Create Page Route:**
    Create `src/app/products/page.tsx`.
    - `async function ProductPage()` (Server Component)
    - Fetch data: `const products = await getProducts();`
    - Render: `<ProductCard key={p.id} product={p} />` inside a grid.

5.  **Form Validation (Optional):**
    If adding a creation form, create `src/schemas/product.ts` using Zod.
    use `react-hook-form` + `zodResolver`.

## ⚙️ Setup & Running

1.  **Install Dependencies:**
    ```bash
    npm install
    ```

2.  **Environment:**
    Copy `.sample.env` to `.env.local` and configure `NEXT_PUBLIC_API_URL`.

3.  **Development Server:**
    ```bash
    npm run dev
    # Running at http://localhost:3000
    ```

4.  **Build used for Production:**
    ```bash
    npm run build
    npm run start
    ```
