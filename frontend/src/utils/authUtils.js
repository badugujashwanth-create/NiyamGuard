function pathnameOnly(path = "/") {
  const value = String(path || "/").split(/[?#]/, 1)[0];
  return value.startsWith("/") ? value : `/${value}`;
}

function isPath(path, root) {
  return path === root || path.startsWith(`${root}/`);
}

const citizenRoots = [
  "/citizen",
  "/services",
  "/apply",
  "/applications",
  "/track",
  "/payment",
  "/scheme-finder",
  "/chatbot",
];

const governmentRoots = ["/government"];
const adminPages = new Set(["/admin", "/admin/sandbox", "/admin/audit", "/admin/users"]);

export function roleHomePath(user) {
  if (!user) return "/login";
  switch (user.role) {
    case "citizen":
      return "/citizen";
    case "officer":
    case "reviewer":
      return "/government";
    case "sandbox_admin":
      return "/admin/sandbox";
    case "admin":
      return "/admin";
    default:
      return "/login";
  }
}

export function canAccessRoute(path, user) {
  if (!user) return false;
  const pathname = pathnameOnly(path);

  if (user.role === "citizen") {
    return citizenRoots.some((root) => isPath(pathname, root));
  }
  if (["officer", "reviewer"].includes(user.role)) {
    return governmentRoots.some((root) => isPath(pathname, root));
  }
  if (user.role === "sandbox_admin") {
    return pathname === "/admin/sandbox";
  }
  if (user.role === "admin") {
    return adminPages.has(pathname);
  }
  return false;
}

export function isPublicRoute(path) {
  const pathname = pathnameOnly(path);
  return (
    pathname === "/" ||
    isPath(pathname, "/portal") ||
    pathname === "/login" ||
    isPath(pathname, "/verify") ||
    isPath(pathname, "/verify-certificate")
  );
}
