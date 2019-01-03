pub mod ray;
pub mod camera;
pub mod scenes;
pub mod hitable;
pub mod material;
pub mod hitrecord;
pub mod colorizer;

/// Crate Reexports
pub mod prelude {
    pub use crate::material::{
        Material,
        Metal,
        Dieletric,
        Lambertian,
        EmptyMaterial
    };
    pub use crate::hitable::{
        HitableList,
        Sphere,
        Hitable,
    };
    pub use crate::ray::Ray;
    pub use crate::colorizer::*;
    pub use crate::camera::Camera;
    pub use crate::scenes::scene_1;
    pub use crate::scenes::scene_2;
    pub use crate::scenes::scene_random;
    pub use crate::hitrecord::HitRecord;
    
    pub type Vector3f = nalgebra::Vector3<f32>;
}