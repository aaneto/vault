use crate::prelude::{
    Vector3f,
    HitRecord,
    HitableList,
    Hitable,
    Ray,
};

pub fn colorize(vec: Vector3f) -> [u8; 3] {
    [(255.9 * vec.x) as u8, (255.9 * vec.y) as u8, (255.9 * vec.z) as u8]
}

pub fn colorize_gamma2(vec: Vector3f) -> [u8; 3] {
    [(255.9 * vec.x.sqrt()) as u8, (255.9 * vec.y.sqrt()) as u8, (255.9 * vec.z.sqrt()) as u8]
}

pub fn color(ray: &Ray, world: &HitableList, depth: u32) -> Vector3f {
    let white = Vector3f::new(1.0, 1.0, 1.0);
    let blue = Vector3f::new(0.5, 0.7, 1.0);
    
    let mut record = HitRecord::new();

    if world.hit(&ray, 0.001, std::f32::MAX, &mut record) {
        let mut scattered = Ray::new();
        let mut attenuation = Vector3f::new(0.0, 0.0, 0.0);

        if depth < 50 && record.material.scatter(ray, &record, &mut attenuation, &mut scattered) {
            let a = &attenuation;
            let b = &color(&scattered, world, depth + 1);

            Vector3f::new(a.x * b.x, a.y * b.y, a.z * b.z)
        }
        else {
            Vector3f::new(0.0, 0.0, 0.0)
        }
    }
    else {
        let unit_direction = nalgebra::normalize(&ray.direction);
        let t: f32 = 0.5 * (unit_direction.y + 1.0);

        (1.0 - t) * white + t * blue
    }
}