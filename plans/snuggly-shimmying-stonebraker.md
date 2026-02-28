# Plan: Custom Headless Clerk Auth Pages (Ollama-style)

## Context

The studio app currently uses Clerk's pre-built `<SignIn />` and `<SignUp />` components which render Clerk's own UI. We want to replace these with fully custom headless auth forms that match Ollama.com's minimal design — centered card, logo above, clean typography — while using Oculis design tokens and NuxtUI components.

Clerk Elements is **not available for Vue/Nuxt** (Next.js only), so we use `useSignIn()` / `useSignUp()` composables from `@clerk/vue` (auto-imported by `@clerk/nuxt`) to build a fully custom headless flow.

## Approach

Use NuxtUI's `UAuthForm` component as the foundation. It provides field configuration, OAuth provider buttons, separator, submit button, validation, loading states, and slots — all pre-styled and accessible. For the OTP verification step, use `UPinInput` with `otp` mode.

Each page has two steps:
1. **Email step** — `UAuthForm` with email field + Google/GitHub providers
2. **Verify step** — form with `UPinInput` OTP input + verify button

## Files to Modify

| File | Action |
|------|--------|
| `apps/studio/pages/sign-in/[...sign-in].vue` | Rewrite — headless sign-in with UAuthForm |
| `apps/studio/pages/sign-up/[...sign-up].vue` | Rewrite — headless sign-up with UAuthForm |

No new files needed. Catch-all routes handle SSO callbacks.

## Implementation

### Sign-In Page (`apps/studio/pages/sign-in/[...sign-in].vue`)

**Script setup:**

```ts
import { AuthenticateWithRedirectCallback } from '@clerk/vue'
import * as z from 'zod'
import type { FormSubmitEvent, AuthFormField } from '@nuxt/ui'

definePageMeta({ layout: false })

const { signIn, isLoaded: isSignInLoaded } = useSignIn()
const clerk = useClerk()
const route = useRoute()

// State machine: 'email' | 'verifying' | 'sso-callback'
const step = ref<'email' | 'verifying' | 'sso-callback'>('email')
const email = ref('')
const error = ref('')
const isSubmitting = ref(false)
const codeValue = ref<string[]>([])

// SSO callback detection (catch-all route captures /sign-in/sso-callback)
const isSsoCallback = computed(() => route.path.includes('sso-callback'))
onMounted(() => { if (isSsoCallback.value) step.value = 'sso-callback' })
```

**Email step — UAuthForm config:**

```ts
const emailFields: AuthFormField[] = [{
  name: 'email',
  type: 'email',
  label: 'Email',
  placeholder: 'Your email address',
  required: true,
}]

const providers = [{
  label: 'Continue with Google',
  icon: 'i-simple-icons-google',
  color: 'neutral' as const,
  variant: 'outline' as const,
  onClick: () => handleOAuth('oauth_google'),
}, {
  label: 'Continue with GitHub',
  icon: 'i-simple-icons-github',
  color: 'neutral' as const,
  variant: 'outline' as const,
  onClick: () => handleOAuth('oauth_github'),
}]

const emailSchema = z.object({
  email: z.string().email('Please enter a valid email'),
})
```

**Handlers:**

```ts
async function handleEmailSubmit(event: FormSubmitEvent<{ email: string }>) {
  error.value = ''
  isSubmitting.value = true
  try {
    email.value = event.data.email
    await signIn.value!.create({ identifier: event.data.email })
    await signIn.value!.prepareFirstFactor({ strategy: 'email_code' })
    step.value = 'verifying'
  } catch (err: any) {
    error.value = err.errors?.[0]?.longMessage || err.message || 'Something went wrong'
  } finally {
    isSubmitting.value = false
  }
}

async function handleVerify() {
  error.value = ''
  isSubmitting.value = true
  try {
    const code = codeValue.value.join('')
    const result = await signIn.value!.attemptFirstFactor({ strategy: 'email_code', code })
    if (result.status === 'complete') {
      await clerk.value!.setActive({ session: result.createdSessionId })
      navigateTo('/builder')
    }
  } catch (err: any) {
    error.value = err.errors?.[0]?.longMessage || err.message || 'Invalid code'
  } finally {
    isSubmitting.value = false
  }
}

async function handleOAuth(strategy: 'oauth_google' | 'oauth_github') {
  try {
    await signIn.value!.authenticateWithRedirect({
      strategy,
      redirectUrl: '/sign-in/sso-callback',
      redirectUrlComplete: '/builder',
    })
  } catch (err: any) {
    error.value = err.errors?.[0]?.longMessage || err.message || 'OAuth error'
  }
}
```

**Template structure:**

```
<main> full-screen centered, bg-primary
  <div> centered container, max-w-sm
    <OculisOwlLogo :size="64" :animate="false" />
    <h1> "Sign in"

    <!-- SSO Callback -->
    <AuthenticateWithRedirectCallback v-if="step === 'sso-callback'" />

    <!-- Loading -->
    <div v-else-if="!isSignInLoaded"> spinner

    <!-- Email Step -->
    <template v-else-if="step === 'email'">
      <UAuthForm
        :fields="emailFields"
        :providers="providers"
        :schema="emailSchema"
        :loading="isSubmitting"
        :submit="{ label: 'Continue', block: true }"
        separator="or"
        @submit="handleEmailSubmit"
      >
        <template #validation v-if="error">
          <UAlert color="error" :title="error" icon="i-heroicons-exclamation-circle" />
        </template>
        <template #footer>
          Don't have an account? <NuxtLink to="/sign-up">Sign up</NuxtLink>
        </template>
      </UAuthForm>
    </template>

    <!-- Verify Step -->
    <template v-else-if="step === 'verifying'">
      <UCard>
        <p>We sent a code to {{ email }}</p>
        <form @submit.prevent="handleVerify">
          <UFormField label="Verification code">
            <UPinInput v-model="codeValue" otp :length="6" type="number" />
          </UFormField>
          <UAlert v-if="error" color="error" :title="error" />
          <UButton type="submit" block :loading="isSubmitting">Verify</UButton>
        </form>
        <button @click="step = 'email'; error = ''">Back</button>
      </UCard>
    </template>
  </div>
</main>
```

**Scoped CSS:** Minimal custom styles using Oculis design tokens for the container, heading, logo spacing, footer link, and back button. NuxtUI components handle their own theming.

### Sign-Up Page (`apps/studio/pages/sign-up/[...sign-up].vue`)

Nearly identical structure. Key differences:
- Uses `useSignUp()` instead of `useSignIn()`
- `signUp.value.create({ emailAddress: email })` (note: `emailAddress` not `identifier`)
- `signUp.value.prepareEmailAddressVerification({ strategy: 'email_code' })`
- `signUp.value.attemptEmailAddressVerification({ code })`
- Title: "Create account"
- OAuth `redirectUrl`: `/sign-up/sso-callback`
- Footer: "Already have an account? Sign in" linking to `/sign-in`

### SSO Callback Handling

Both pages use catch-all routes (`[...sign-in].vue`, `[...sign-up].vue`). When OAuth redirects to `/sign-in/sso-callback`, the catch-all page loads and detects `sso-callback` in the path. It renders `<AuthenticateWithRedirectCallback />` (imported from `@clerk/vue`) which handles the OAuth completion and redirect to `/builder`.

### Zod Dependency

`UAuthForm` uses Zod for validation. Check if `zod` is already installed; if not, add it: `pnpm --filter studio add zod`

## NuxtUI Components Used

- `UAuthForm` — main form component with fields, providers, separator, submit, validation/footer slots
- `UPinInput` — OTP code input with `otp` prop for mobile autocomplete
- `UFormField` — wraps PinInput with label for verification step
- `UCard` — container for verification step
- `UAlert` — error message display
- `UButton` — verify button, back button

## Verification

1. `pnpm --filter studio build` — Nuxt production build succeeds
2. `pnpm --filter studio lint` — no lint errors
3. `pnpm --filter studio format` — formatting clean
4. `pnpm test` — all tests pass
5. Manual: navigate to `/sign-in`, verify email form renders with owl logo
6. Manual: enter email, verify OTP step with PinInput appears
7. Manual: click OAuth buttons, verify redirect flows
8. Manual: check `/sign-up` has same structure with cross-link to sign-in
9. Manual: verify dark mode theming looks correct
