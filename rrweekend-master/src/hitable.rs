use std::rc::Rc;

use crate::prelude::{
    Vector3f,
    Material,
    HitRecord,
    Ray,
};

pub trait Hitable {
    fn hit(&self, ray: &Ray, t_min: f32, t_max: f32, hit_record: &mut HitRecord) -> bool;
}

pub struct Sphere {
    pub center: Vector3f,
    pub radius: f32,
    pub material: Rc<Material>,
}

impl Hitable for Sphere {
    fn hit(&self, ray: &Ray, t_min: f32, t_max: f32, hit_record: &mut HitRecord) -> bool {
        let oc = ray.origin - self.center;
        let a = nalgebra::dot(&ray.direction, &ray.direction);
        let b = 2.0 * nalgebra::dot(&oc, &ray.direction);
        let c = nalgebra::dot(&oc, &oc) - self.radius * self.radius;

        let discriminant = b * b - 4.0 * a * c;

        if discriminant > 0.0 {
            let temp = (-b - discriminant.sqrt()) / (2.0 * a);
            if temp < t_max && temp > t_min {
                hit_record.t = temp;
                hit_record.material = Rc::clone(&self.material);
                hit_record.contact = ray.point_at_parameter(hit_record.t);
                hit_record.normal = (hit_record.contact - self.center) / self.radius;

                return true;
            }
            let temp = (-b + discriminant.sqrt()) / (2.0 * a);
            
            if temp < t_max && temp > t_min {
                hit_record.t = temp;
                hit_record.material = Rc::clone(&self.material);
                hit_record.contact = ray.point_at_parameter(hit_record.t);
                hit_record.normal = (hit_record.contact - self.center) / self.radius;

                return true;
            }

        }

        false
    }
}

pub struct HitableList {
    pub list: Vec<Box<Hitable>>,
}

impl HitableList {
    pub fn new() -> Self {
        HitableList {
            list: Vec::new(),
        }
    }
}

impl Hitable for HitableList {
    fn hit(&self, ray: &Ray, t_min: f32, t_max: f32, hit_record: &mut HitRecord) -> bool {
        let mut temp_record = HitRecord::new();
        
        let mut hit_anything = false;
        let mut closest_so_far = t_max;
        
        for i in 0..self.list.len() {
            if self.list[i].hit(&ray, t_min, closest_so_far, &mut temp_record) {
                hit_anything = true;
                closest_so_far = temp_record.t;

                hit_record.contact = temp_record.contact;
                hit_record.normal = temp_record.normal;
                hit_record.material = Rc::clone(&temp_record.material);
                hit_record.t = temp_record.t;
            }
        }

        hit_anything
    }
}