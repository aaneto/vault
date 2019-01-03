use rand::Rng;

use crate::prelude::{
    Vector3f,
    Ray,
};

fn random_in_unit_disk() -> Vector3f {
    let mut rng = rand::thread_rng();
    loop {
        let r1: f32 = rng.gen();
        let r2: f32 = rng.gen();

        let p = Vector3f::new(2.0 * r1 - 1.0, 2.0 * r2 - 1.0, 0.0);

        if p.x * p.x + p.y * p.y < 1.0 {
            return p;
        }
    }
}

pub struct Camera {
    origin: Vector3f,
    horizontal: Vector3f,
    vertical: Vector3f,
    lower_left_corner: Vector3f,
    u: Vector3f,
    v: Vector3f,
    w: Vector3f,
    lens_radius: f32,
}

impl Camera {
    pub fn new(
        lookfrom: Vector3f,
        lookat: Vector3f,
        vup: Vector3f,
        vfov: f32,
        aspect_ratio: f32,
        focus_distance: f32,
        aperture: f32,
        ) -> Self {

        let theta: f32 = vfov * std::f32::consts::PI / 180.0;
        let half_height = (theta / 2.0).tan();
        let half_width = aspect_ratio * half_height;

        let w = nalgebra::normalize(&(lookfrom - lookat));
        let u = vup.cross(&w);
        let v = w.cross(&u);

        Camera {
            origin: lookfrom,
            lower_left_corner: lookfrom - w * focus_distance - u * half_width * focus_distance - v * half_height * focus_distance,
            vertical: 2.0 * half_height * focus_distance * v,
            horizontal: 2.0 * half_width * focus_distance * u,
            lens_radius: aperture / 2.0,
            u,
            v,
            w,
        }
    }

    pub fn get_ray(&self, s: f32, t: f32) -> Ray {
        let rd = self.lens_radius * random_in_unit_disk();
        let offset = self.u * rd.x + self.v * rd.y;
        Ray {
            origin: self.origin + offset,
            direction: self.lower_left_corner + s * self.horizontal + t * self.vertical - self.origin - offset
        }
    }
}