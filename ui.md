# UI Gaps and Improvement Plan

This document outlines the current gaps in the CamFindAI frontend and provides a roadmap for enhancing the user interface, improving user experience, and modernizing the design aesthetic without impacting backend operations.

## 1. General Aesthetics & Design System
* **Premium Feel**: While the `glass-panel` approach is a good start, the overall aesthetic can be elevated. Use deeper, richer gradients, more nuanced shadow layering (e.g., multiple layered box-shadows), and refined typography.
* **Micro-interactions**: Many interactive elements (buttons, list items) lack subtle feedback. Implement hover states that slightly scale the element (`hover:scale-[1.02]`) or reveal subtle glows using Tailwind's `group-hover`.
* **Empty States**: Currently, empty states (e.g., "No cameras currently online" in `LiveView`) are functional but uninspiring. They should feature custom SVG illustrations or animated icons (e.g., Lottie) to make the app feel alive even when data is sparse.
* **Skeleton Loaders**: Add skeleton loading states for asynchronous data fetching instead of sudden content popping or basic text loading indicators.

## 2. Layout & Navigation (`Layout.tsx`)
* **Mobile Responsiveness**: The sidebar is currently hidden on mobile devices (`hidden md:flex`), but there is no alternative navigation provided for small screens. 
  * *Improvement*: Implement a hamburger menu that toggles a slide-out drawer or a bottom navigation bar for mobile users.
* **System Status Indicator**: The "System Online" indicator is static text with a blinking dot. It should dynamically reflect the actual backend WebSocket or API health status.

## 3. Live View operations (`LiveView.tsx`)
* **Grid Layout Controls**: The current grid layout is hardcoded based on screen size (`grid-cols-1 lg:grid-cols-2 xl:grid-cols-3`).
  * *Improvement*: Add UI controls allowing users to select grid layouts (e.g., 1x1, 2x2, 3x3, 4x4) regardless of screen size.
* **Camera Controls**: There is no way to expand a specific camera feed to full-screen. 
  * *Improvement*: Add a "Fullscreen" or "Theater Mode" toggle on each camera feed.
* **Feed Error Handling**: The live feed relies on an `<img>` tag refreshing via WebSocket. If frames drop or the connection stutters, there is no visual feedback to the user other than a frozen image. Show a brief "Reconnecting..." or buffering overlay.

## 4. Camera Management (`CameraManagement.tsx`)
* **Form UX**: The "Add Camera" form simply pushes content down.
  * *Improvement*: Migrate the form into a sleek Modal overlay or a right-side sliding Drawer to keep the primary view clean.
* **Validation & Error Handling**: Form validation relies entirely on native HTML `required` attributes. Implement comprehensive inline validation (e.g., checking if the RTSP URL format is valid) and display toast notifications for API success/errors.
* **Health Sparklines**: The current CSS-based sparkline for FPS is creative but lacks interactivity.
  * *Improvement*: Replace it with a lightweight charting library (like Recharts) to allow users to hover over data points and see exact timestamps and FPS values.

## 5. Cross-Camera Timeline (`Timeline.tsx`)
* **Visualizing Trajectory**: The timeline currently lists events sequentially. 
  * *Improvement*: Introduce a "Node Graph" or a conceptual floor plan view showing how an identity moved from Camera A to Camera B visually.
* **Event Thumbnails**: The timeline entries lack visual context. 
  * *Improvement*: Display a small cropped snapshot (thumbnail) of the identity at the specific timestamp to verify the tracking accuracy visually.
* **Filtering & Search**: There is no way to filter the timeline by specific date ranges, shifts, or specific camera zones.

## 6. Real-time Alerts & Notifications
* **Global Notifications**: There is currently no global toast notification system. If a high-priority tracking event or camera failure occurs while the user is on the Settings page, they won't know.
  * *Improvement*: Implement a global Toast Provider (e.g., `react-hot-toast` or `sonner`) tied to the WebSocket to push critical alerts immediately across all pages.

## Summary Checklist for Next Steps
- [ ] Implement Mobile Navigation (Drawer/Hamburger).
- [ ] Add Layout Controls to Live View (Grid size, Fullscreen).
- [ ] Move Camera Form to a Modal/Drawer with better validation.
- [ ] Add thumbnails to Timeline events.
- [ ] Set up a Global Toast Notification system.
- [ ] Polish UI with advanced hover states, better empty states, and skeleton loaders.
