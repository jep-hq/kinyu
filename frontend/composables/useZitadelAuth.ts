import { UserManager, WebStorageStateStore, User } from 'oidc-client-ts';

// Configuration (Move to runtimeConfig in production)
const zitadelConfig = {
  authority: "http://localhost:8080",
  client_id: "your-client-id-from-setup-script",
  redirect_uri: "http://localhost:3000/backoffice/callback",
  post_logout_redirect_uri: "http://localhost:3000",
  response_type: "code",
  scope: "openid profile email urn:zitadel:iam:org:project:roles",
};

// Singleton instance, lazy initialized
let userManager: UserManager | null = null;

function getUserManager() {
    if (!process.client) return null;
    if (!userManager) {
        userManager = new UserManager({
            ...zitadelConfig,
            userStore: new WebStorageStateStore({ store: window.localStorage }),
        });
    }
    return userManager;
}

export const useZitadelAuth = () => {
    const user = useState<User | null>('zitadel_user', () => null);
    const userGrants = useState<any[]>('zitadel_grants', () => []);

    const login = async () => {
        const mgr = getUserManager();
        if (mgr) await mgr.signinRedirect();
    };

    const handleCallback = async () => {
        const mgr = getUserManager();
        if (mgr) {
            const u = await mgr.signinRedirectCallback();
            user.value = u;
            return u;
        }
    };

    const switchTenant = async (orgId: string) => {
        const mgr = getUserManager();
        if (mgr) {
            // Token Swap: Request new access token with specific Org ID scope
            await mgr.signinRedirect({
                scope: `${zitadelConfig.scope} urn:zitadel:iam:org:id:${orgId}`
            });
        }
    };

    const fetchGrants = async () => {
        if (!user.value?.access_token) return;
        try {
            // Query Zitadel for my memberships
            const response = await fetch(`${zitadelConfig.authority}/auth/v1/users/me/grants`, {
                headers: { Authorization: `Bearer ${user.value.access_token}` }
            });
            const data = await response.json();
            userGrants.value = data.result || [];
        } catch (e) {
            console.error("Failed to fetch grants", e);
        }
    };

    // On client init, check if we have a user in storage
    if (process.client) {
        const mgr = getUserManager();
        mgr?.getUser().then((u) => {
             if (u && !u.expired) user.value = u;
        });
    }

    const currentTenantId = computed(() => {
        // Zitadel puts the org ID in this claim when scoped
        return user.value?.profile["urn:zitadel:iam:org:id"];
    });

    return {
        user,
        userGrants,
        currentTenantId,
        login,
        handleCallback,
        switchTenant,
        fetchGrants
    };
};
