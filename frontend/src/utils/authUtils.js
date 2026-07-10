export function roleHomePath(user) {
  if (!user) return "/login";
  switch (user.role) {
    case "citizen":
      return "/citizen";
    case "officer":
    case "reviewer":
    case "admin":
      return "/government";
    case "sandbox_admin":
      return "/sandbox";
    default:
      return "/login";
  }
}

export function canAccessRoute(path, user) {
  if (!user) return false;
  if (path.startsWith("/citizen")) {
    return user.role === "citizen" || user.role === "admin";
  }
  if (path.startsWith("/government") || path.startsWith("/officer")) {
    return ["officer", "reviewer", "admin"].includes(user.role);
  }
  if (path.startsWith("/sandbox") || path.startsWith("/virtual-gov")) {
    return user.role === "sandbox_admin" || user.role === "admin";
  }
  if (path.startsWith("/chatbot")) {
    return true;
  }
  if (path.startsWith("/admin")) {
    return ["admin", "reviewer", "officer"].includes(user.role);
  }
  if (
    path.startsWith("/services") ||
    path.startsWith("/apply") ||
    path.startsWith("/applications") ||
    path.startsWith("/track") ||
    path.startsWith("/verify-certificate") ||
    path.startsWith("/payment")
  ) {
    return user.role === "citizen" || user.role === "admin";
  }
  return true;
}

export function isPublicRoute(path) {
  return (
    path === "/login" ||
    path.startsWith("/demo") ||
    path.startsWith("/mock/") ||
    path.startsWith("/scheme-finder")
  );
}
