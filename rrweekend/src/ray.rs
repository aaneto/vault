use crate::prelude::Vector3f;

pub struct Ray {
    pub origin: Vector3f,
    pub direction: Vector3f,
}

impl Ray {
    pub fn new() -> Self {
        Ray {
            origin: Vector3f::new(0.0, 0.0, 0.0),
            direction: Vector3f::new(0.0, 0.0, 0.0),
        }
    }

    pub fn point_at_parameter(&self, t: f32) -> Vector3f {
        self.origin + t * self.direction
    }
}