use rand::Rng;

use crate::prelude::{
    Vector3f,
    HitRecord,
    Ray
};

fn random_in_unit_sphere() -> Vector3f {
    let mut rng = rand::thread_rng();
    loop {
        let r1: f32 = rng.gen();
        let r2: f32 = rng.gen();
        let r3: f32 = rng.gen();

        let p = Vector3f::new(2.0 * r1 - 1.0, 2.0 * r2 - 1.0, 2.0 * r3 - 1.0);

        if p.x * p.x + p.y * p.y + p.z * p.z < 1.0 {
            return p;
        }
    }
}

pub trait Material {
    fn scatter(&self, ray_in: &Ray, hit_record: &HitRecord, attenuation: &mut Vector3f, scattered: &mut Ray) -> bool;
}


pub struct Lambertian {
    pub albedo: Vector3f,
}

impl Material for Lambertian {
        fn scatter(&self, _: &Ray, record: &HitRecord, attenuation: &mut Vector3f, scattered: &mut Ray) -> bool {
        let target = record.contact + record.normal + random_in_unit_sphere();

        scattered.origin = record.contact;
        scattered.direction = target - record.contact;
        
        attenuation.x = self.albedo.x;
        attenuation.y = self.albedo.y;
        attenuation.z = self.albedo.z;

        true
    }
}

fn reflect(v: &Vector3f, n: &Vector3f) -> Vector3f {
    v - 2.0 * nalgebra::dot(v, n) * n
}

fn refract(v: &Vector3f, n: &Vector3f, ni_over_nt: f32, refracted: &mut Vector3f) -> bool {
    let uv = nalgebra::normalize(v);
    let dt = nalgebra::dot(&uv, n);
    let discriminant = 1.0 - ni_over_nt * ni_over_nt * (1.0 - dt * dt);
    
    if discriminant > 0.0 {
        let res = ni_over_nt * (uv - n * dt) - n * discriminant.sqrt();
        refracted.x = res.x;
        refracted.y = res.y;
        refracted.z = res.z;
        true
    } else {
        false
    }
}

fn schlick(cosine: f32, ref_idx: f32) -> f32 {
    let r0 = (1.0 - ref_idx) / (1.0 + ref_idx);
    let r0 = r0 * r0;

    r0 + (1.0 - r0) * (1.0 - cosine).powf(5.0)
}

pub struct Dieletric {
    pub ref_idx: f32,
}

impl Material for Dieletric {
    fn scatter(&self, ray_in: &Ray, record: &HitRecord, attenuation: &mut Vector3f, scattered: &mut Ray) -> bool {
        let mut outward_normal = Vector3f::new(0.0, 0.0, 0.0);
        let reflected = reflect(&ray_in.direction, &record.normal);
        let ni_over_nt: f32;
        let cosine: f32;
        let reflect_prob: f32;
        let mut rng = rand::thread_rng();

        attenuation.x = 1.0;
        attenuation.y = 1.0;
        attenuation.z = 1.0;

        let mut refracted = Vector3f::new(0.0, 0.0, 0.0);
        
        if nalgebra::dot(&ray_in.direction, &record.normal) > 0.0 {
            outward_normal.x = -record.normal.x;
            outward_normal.y = -record.normal.y;
            outward_normal.z = -record.normal.z;

            ni_over_nt = self.ref_idx;

            cosine = self.ref_idx * nalgebra::dot(&ray_in.direction, &record.normal) / nalgebra::magnitude(&ray_in.direction);

        } else {
            outward_normal.x = record.normal.x;
            outward_normal.y = record.normal.y;
            outward_normal.z = record.normal.z;

            ni_over_nt = 1.0 / self.ref_idx;
            cosine = -nalgebra::dot(&ray_in.direction, &record.normal) / nalgebra::magnitude(&ray_in.direction);
        }

        if refract(&ray_in.direction, &outward_normal, ni_over_nt, &mut refracted) {
            reflect_prob = schlick(cosine, self.ref_idx);
        } else {
            reflect_prob = 1.0;
        }
        
        if rng.gen::<f32>() < reflect_prob {
            scattered.origin = record.contact;
            scattered.direction = reflected;
        } else {
            scattered.origin = record.contact;
            scattered.direction = refracted;
        }
        true
    }
}

pub struct Metal {
    pub albedo: Vector3f,
    pub fuzz: f32,
}

impl Material for Metal {
    fn scatter(&self, ray_in: &Ray, record: &HitRecord, attenuation: &mut Vector3f, scattered: &mut Ray) -> bool {
        let reflected = reflect(&nalgebra::normalize(&ray_in.direction), &record.normal);
        
        scattered.origin = record.contact;
        scattered.direction = reflected + self.fuzz * random_in_unit_sphere();

        attenuation.x = self.albedo.x;
        attenuation.y = self.albedo.y;
        attenuation.z = self.albedo.z;

        nalgebra::dot(&scattered.direction, &record.normal) > 0.0
    }
}

pub struct EmptyMaterial{}
impl Material for EmptyMaterial {
    fn scatter(&self, _: &Ray,_: &HitRecord, _: &mut Vector3f, _: &mut Ray) -> bool {
        false
    }   
}
