use std::rc::Rc;

use crate::prelude::{
    Material,
    EmptyMaterial,
    Vector3f,
};

pub struct HitRecord {
    pub t: f32,
    pub contact: Vector3f,
    pub normal: Vector3f,
    pub material: Rc<Material>,
}

impl HitRecord {
    pub fn new() -> Self {
        HitRecord {
            t: 0.0,
            contact: Vector3f::new(0.0, 0.0, 0.0),
            normal: Vector3f::new(0.0, 0.0, 0.0),
            material: Rc::new(EmptyMaterial{}),
        }
    }
}