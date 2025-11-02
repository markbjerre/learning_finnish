# Welcome to your Lovable project

## Project info

**URL**: https://lovable.dev/projects/1f40692c-cca4-4916-b08d-d5818e2b22fe

## ⚠️ Environment Setup (IMPORTANT)

This project requires environment variables. Before running:

1. **Create `.env` file** from template:
   ```sh
   cp .env.example .env
   ```

2. **Add your OpenAI API key** to `.env`:
   ```env
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

3. **Get your OpenAI key**: https://platform.openai.com/api-keys

### 🚀 Migration Note

**Before deploying to VPS:**
- Move `OPENAI_API_KEY` from project `.env` to `backend/.env`
- This keeps the API key secure on the backend server
- Frontend `.env` should only contain `VITE_API_URL`

See `backend/README.md` for deployment instructions.

---

## How can I edit this code?

There are several ways of editing your application.

**Use Lovable**

Simply visit the [Lovable Project](https://lovable.dev/projects/1f40692c-cca4-4916-b08d-d5818e2b22fe) and start prompting.

Changes made via Lovable will be committed automatically to this repo.

**Use your preferred IDE**

If you want to work locally using your own IDE, you can clone this repo and push changes. Pushed changes will also be reflected in Lovable.

The only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory.
cd <YOUR_PROJECT_NAME>

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Set up environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Step 5: Start the development server with auto-reloading and an instant preview.
npm run dev
```

**Edit a file directly in GitHub**

- Navigate to the desired file(s).
- Click the "Edit" button (pencil icon) at the top right of the file view.
- Make your changes and commit the changes.

**Use GitHub Codespaces**

- Navigate to the main page of your repository.
- Click on the "Code" button (green button) near the top right.
- Select the "Codespaces" tab.
- Click on "New codespace" to launch a new Codespace environment.
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

**Backend:**
- Flask (Python)
- OpenAI API for AI-powered Finnish word lookup
- Gunicorn + Docker for deployment

See `backend/README.md` and `DEPLOYMENT.md` for backend details.

## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/1f40692c-cca4-4916-b08d-d5818e2b22fe) and click on Share -> Publish.

## Can I connect a custom domain to my Lovable project?

Yes, you can!

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

Read more here: [Setting up a custom domain](https://docs.lovable.dev/features/custom-domain#custom-domain)
