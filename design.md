# L1 DataLab Studio : Stratégie Produit & Design

## 1. Vision Stratégique
Le **L1 DataLab Studio** n'est pas un simple projet étudiant ni un dashboard administratif classique. Il s'agit d'une plateforme d'**Analytics Prédictif Premium** qui doit projeter l'image d'une véritable Startup AI (Machine Learning as a Service).

Pour le jury RNCP, les recruteurs ou le portfolio GitHub, le visuel doit immédiatement transmettre :
- Profondeur technique (ML, Data Engineering, Infrastructure distribuée).
- Intelligence (Temps réel, Agents LLM, RAG).
- Qualité perçue (Premium, Fluide, Exigeant).

Inspirations directes : *Linear*, *Vercel*, *Anthropic*, *Stripe*.

## 2. Palette de Couleurs "Sunset Mystique"
Le projet adopte une identité visuelle calme, mystérieuse et moderne, tranchant avec les interfaces sportives "gaming" classiques.

- **Deep Navy** (`#010108`) : Fond principal. Mystérieux, profond.
- **Midnight Purple** (`#20115b`) : Couleur secondaire, apporte de la structure sans utiliser le gris basique.
- **Electric Violet** (`#7232f2`) : Accentuation pour les éléments interactifs.
- **Neon Lilas** (`#c876ff`) : Glows, lueurs internes, effets de survol.
- **Sunset Pink** (`#f6b3e5`) : Touches finales, rappelle le ciel couchant.

## 3. Direction Artistique : "Liquidglass"
Nous avons fait évoluer le *Glassmorphism* vers le **Liquidglass** :
- **Bordures lumineuses** : Dégradés très fins (`border-white/10` ou `sunset-primary/30`).
- **Glow directionnel** : Flous d'arrière-plan colorés positionnés sous les composants (`blur-[100px]`).
- **Minimalisme** : Peu de bordures dures, utilisation de l'espace négatif, polices claires et aérées.
- Focus absolu sur "Qualité > Quantité".

## 4. Animation & Motion Design (GSAP)
Le Motion Design est le vrai différenciateur. Nous utilisons **GSAP + ScrollTrigger** pour transformer la Landing Page en une expérience narrative cinématique :
- **Pinning** : Fixer des éléments centraux (ex: Dashboard preview) pendant que le texte défile.
- **Scrubbing** : Lier l'animation directement à la position du scroll pour une sensation de contrôle absolu.
- **Micro-interactions** : Hover avec profondeur, loading states élégants (`Running Neural Network...`).
