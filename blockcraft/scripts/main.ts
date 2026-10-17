// Clouds drift east and wrap around the island; movement is the native walk camera.
import { component, field, game, system } from "amoris";

const SPAN = 120; // metres a cloud travels before it wraps to the west edge

export const Cloud = component("Cloud", {
    version: 1, doc: "A cloud drifting with the wind.",
    fields: { speed: field.f64(1, "Drift speed, m/s.") },
});

export const drift = system({
    name: "drift", phase: "update", doc: "Moves each cloud east, wrapping at the edge.",
    queries: { clouds: { with: ["Cloud", "Transform"], fields: ["Cloud.speed", "Transform.position"] } },
    run(ctx, { clouds }) {
        const speed = clouds.cols.Cloud.speed;
        const x = clouds.cols.Transform.position.x;
        for (let r = 0; r < clouds.len; r++) {
            x[r] += speed[r] * ctx.dt;
            if (x[r] > SPAN / 2) x[r] -= SPAN;
        }
    },
});

export default game({ components: [Cloud], systems: [drift] });
