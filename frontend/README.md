# SkillSync AI Frontend

The SkillSync AI frontend is a React + Vite application using JavaScript and Material UI. It currently includes the shared architecture, public marketing landing page, and frontend-only authentication experience. It intentionally contains no dashboard, backend endpoint definitions, mock API responses, or real authentication-provider integration.

## Prerequisites

- A current Node.js LTS release supported by Vite
- npm

## Run locally

```bash
cd skillsync-ai/frontend
npm install
cp .env.example .env.local
npm run dev
```

On Windows PowerShell installations where `npm` scripts are disabled, use `npm.cmd` instead:

```powershell
npm.cmd install
Copy-Item .env.example .env.local
npm.cmd run dev
```

The Vite server prints the local URL after it starts.

## Available scripts

```bash
npm run dev      # Start the development server
npm run build    # Create a production build
npm run preview  # Preview the production build
npm run lint     # Lint JavaScript and JSX files
```

## Environment variables

Vite exposes only variables prefixed with `VITE_` to browser code. Copy `.env.example` to `.env.local` for local overrides.

| Variable | Required | Purpose |
| --- | --- | --- |
| `VITE_APP_NAME` | No | Application name used in the shell; defaults to `SkillSync AI`. |
| `VITE_API_BASE_URL` | No | Optional Axios base URL. Leave unset until an approved backend contract is available. |

No API endpoints or authentication headers are configured in this phase.

## Architecture

```text
src/
├── app/                  # Application-wide providers, routing, and theme
├── features/             # Self-contained business features
│   ├── auth/             # Frontend-only authentication forms and route guard
│   ├── dashboard/        # Reserved; intentionally unimplemented
│   ├── landing/          # Public landing-page sections and composition
│   └── system/           # Application placeholder and not-found route
├── shared/               # Reusable, feature-agnostic modules
│   ├── api/              # Axios client
│   ├── config/           # Environment configuration
│   ├── query/            # TanStack Query client factory
│   └── ui/               # Layout and feedback components
├── App.jsx               # Composition root
└── main.jsx              # Browser entry point
```

Use the `@` import alias for `src`, for example `@/shared/api/apiClient`.

### Shared conventions

- Put feature-specific routes, components, hooks, and API adapters inside `src/features/<feature>/`.
- Keep cross-feature UI, configuration, and infrastructure in `src/shared/`.
- Use `apiClient` only after backend contracts are approved; add endpoint-specific calls inside their owning feature.
- Use TanStack Query for server state and its existing client defaults unless a feature has a documented reason to override them.
- Use `useThemeMode()` in shared or feature UI that needs to change the persisted light/dark mode.
- Keep public landing-page sections in `src/features/landing/`; the shared app shell owns the navbar and footer.
- Use the shared `Reveal` component for restrained entrance/reveal motion. It respects reduced-motion preferences.

## Authentication frontend

The public authentication routes are `/login`, `/register`, and `/forgot-password`. Forms use React Hook Form with Zod validation, accessible password visibility controls, and submission loading/error states.

`src/features/auth/api/authService.js` is an adapter boundary. Its current gateway intentionally throws `AuthIntegrationUnavailableError` after local validation; it makes no HTTP requests and assumes no endpoint or response shape. Replace that gateway only after the backend authentication contract is approved.

`AuthProvider` exposes a temporary unauthenticated session (`user: null`) and `RequireAuth` protects the `/protected` route. No user object or successful sign-in response is fabricated.
