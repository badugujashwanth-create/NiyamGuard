import { getAccessToken, getStoredUser } from "../services/api";
import { canAccessRoute, isPublicRoute, roleHomePath } from "../utils/authUtils";

export default function AuthGuard({ path, children, onRedirect }) {
  const user = getStoredUser();
  const token = getAccessToken();

  if (isPublicRoute(path)) {
    return children;
  }

  if (!token || !user) {
    const next = encodeURIComponent(path);
    onRedirect(`/login?next=${next}`);
    return null;
  }

  if (!canAccessRoute(path, user)) {
    onRedirect(roleHomePath(user));
    return null;
  }

  return children;
}
