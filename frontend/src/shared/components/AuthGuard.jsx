import { getStoredUser, hasAuthSession } from "../../services/api";
import { canAccessRoute, isPublicRoute, roleHomePath } from "../utils/authUtils";

export default function AuthGuard({ path, children, onRedirect }) {
  const user = getStoredUser();

  if (isPublicRoute(path)) {
    return children;
  }

  if (!hasAuthSession() || !user) {
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
