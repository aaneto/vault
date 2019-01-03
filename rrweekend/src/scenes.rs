use rand::rngs::StdRng;
use rand::{
    SeedableRng,
    Rng,
};


use std::rc::Rc;

use crate::prelude::{
    Vector3f,
    Sphere,
    HitableList,
    Lambertian,
    Metal,
    Dieletric,
};

pub fn scene_1() -> HitableList {
    let mut world = HitableList::new();

    let s1 = Sphere {
        center: Vector3f::new(0.0, 0.0, -1.0),
        radius: 0.5,
        material: Rc::new(Lambertian {
            albedo: Vector3f::new(0.6, 0.6, 0.5)
        }),
    };

    let s2 = Sphere {
        center: Vector3f::new(0.0, -100.5, -1.0),
        radius: 100.0,
        material: Rc::new(Lambertian {
            albedo: Vector3f::new(0.8, 0.8, 0.0),
        }),
    };

    let s3 = Sphere {
        center: Vector3f::new(1.0, 0.0, -1.0),
        radius: 0.5,
        material: Rc::new(Metal {
            albedo: Vector3f::new(0.8, 0.6, 0.2),
            fuzz: 1.5,
        }),
    };

    let s4 = Sphere {
        center: Vector3f::new(-1.0, 0.0, -1.0),
        radius: -0.45,
        material: Rc::new(Dieletric {
            ref_idx: 1.5,
        }),
    };

    let s5 = Sphere {
        center: Vector3f::new(-1.0, 0.0, -1.0),
        radius: 0.5,
        material: Rc::new(Dieletric {
            ref_idx: 1.5,
        }),
    };

    world.list.push(Box::new(s1));
    world.list.push(Box::new(s2));
    world.list.push(Box::new(s3));
    world.list.push(Box::new(s4));
    world.list.push(Box::new(s5));

    world
}

pub fn scene_2() -> HitableList {
    let mut world = HitableList::new();

    let r = (std::f32::consts::PI / 4.0).cos();

    let s1 = Sphere {
        center: Vector3f::new(r, 0.0, -1.0),
        radius: r,
        material: Rc::new(Lambertian {
            albedo: Vector3f::new(1.0, 0.0, 0.0)
        }),
    };

    let s2 = Sphere {
        center: Vector3f::new(-r, 0.0, -1.0),
        radius: r,
        material: Rc::new(Lambertian {
            albedo: Vector3f::new(0.0, 0.0, 1.0),
        }),
    };

    world.list.push(Box::new(s1));
    world.list.push(Box::new(s2));

    world
}

pub fn scene_random(seed: &[u8; 32]) -> HitableList {
    let mut world = HitableList::new();
    let mut rng: StdRng = SeedableRng::from_seed(*seed);

    for a in -11..11 {
        for b in -11..11 {
            let choose_mat: f32 = rng.gen();
            let center = Vector3f::new(
                a as f32 + 0.9 * rng.gen::<f32>(),
                0.2,
                b as f32 + 0.9 * rng.gen::<f32>()
            );

            if (center - Vector3f::new(4.0, 0.2, 0.0)).magnitude() > 0.9 { 
                if choose_mat < 0.8 {  // diffuse
                    let s = Sphere {
                        center,
                        radius: 0.2,
                        material: Rc::new( Lambertian {
                            albedo: Vector3f::new(
                                rng.gen::<f32>() * rng.gen::<f32>(),
                                rng.gen::<f32>() * rng.gen::<f32>(),
                                rng.gen::<f32>() * rng.gen::<f32>(),
                            )
                        })
                    };

                    world.list.push(Box::new(s));
                }
                else if choose_mat < 0.95 {
                    let s =  Sphere {
                        center,
                        radius: 0.2,
                        material: Rc::new( Metal {
                            albedo: Vector3f::new(
                                0.5 * (1.0 + rng.gen::<f32>()),
                                0.5 * (1.0 + rng.gen::<f32>()),
                                0.5 * (1.0 + rng.gen::<f32>()),
                            ),
                            fuzz: 0.5 * rng.gen::<f32>(),
                        })
                    };
                    world.list.push(Box::new(s));
                }
                else {
                    let s = Sphere {
                        center,
                        radius: 0.2,
                        material: Rc::new( Dieletric {
                            ref_idx: 1.5
                        })
                    };

                    world.list.push(Box::new(s));
                }
            }
        }

        let s0 = Sphere {
            center: Vector3f::new(0.0, -1000.0, 0.0),
            radius: 1000.0,
            material: Rc::new(Lambertian {
                albedo: Vector3f::new(0.5, 0.5, 0.5)
            }),
        };

        let s1 = Sphere {
            center: Vector3f::new(0.0, 1.0, 0.0),
            radius: 1.0,
            material: Rc::new( Dieletric {
                    ref_idx: 1.5
                }
            )
        };

        let s2 = Sphere {
            center: Vector3f::new(-4.0, 1.0, 0.0),
            radius: 1.0,
            material: Rc::new( Lambertian {
                albedo: Vector3f::new(
                    0.4,
                    0.2,
                    0.1,
                )
            })
        };


        let s3 = Sphere {
            center: Vector3f::new(4.0, 1.0, 0.0),
            radius: 1.0,
            material: Rc::new( Metal {
                albedo: Vector3f::new(
                    0.7,
                    0.6,
                    0.5,
                ),
                fuzz: 0.0,
            })
        };

        world.list.push(Box::new(s0));
        world.list.push(Box::new(s1));
        world.list.push(Box::new(s2));
        world.list.push(Box::new(s3));
    }

    world
}