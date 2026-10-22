import { type RouteConfig, index, layout, route } from "@react-router/dev/routes"

export default [
    index("home/HomeRedirect.tsx"),
    route("login", "login/LoginPage.tsx"),
    layout("login/RequireSession.tsx", [
        route("characters", "character_list/CharacterListPage.tsx"),
        route("characters/new", "character_creation/CharacterCreationPage.tsx"),
        route("characters/:id", "character_sheet/CharacterSheetPage.tsx"),
    ]),
] satisfies RouteConfig
