// Lets TypeScript resolve `import dict from "./locales/xx.yaml"` when using
// @modyfi/vite-plugin-yaml (or an equivalent). Copy into the app's src/.
declare module "*.yaml" {
  const value: Record<string, unknown>;
  export default value;
}
