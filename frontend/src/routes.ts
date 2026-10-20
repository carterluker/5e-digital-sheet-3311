import { type RouteConfig, route } from "@react-router/dev/routes"

export default [
    route("login", "login/LoginPage.tsx"),
    route("characters", "character_list/CharacterListPage.tsx"),
    route("characters/:id", "character_sheet/CharacterSheetPage.tsx"),
] satisfies RouteConfig
