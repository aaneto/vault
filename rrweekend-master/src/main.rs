const WIDTH: u32 = 1200;
const HEIGHT: u32 = 800;

const ASPECT_RATIO: f32 = WIDTH as f32 / HEIGHT as f32;
const VFOV: f32 = 20.0;
const SAMPLES: u32 = 80;
const N_THREADS: u32 = 16;

const CLOSE_THREAD: u32 = 9999;
const LINES_PER_THREAD: u32 = 50;

use std::thread;
use std::sync::Arc;
use std::sync::Mutex;
use std::sync::mpsc::channel;

use rand::Rng;
use raytracing::prelude::*;

fn main() {
    let mut imgbuf = image::ImageBuffer::new(WIDTH, HEIGHT);

    let (tx, rx) = channel();

    let (job_tx, job_rx) = channel();
    let job_rx = Arc::new(Mutex::new(job_rx));

    let mut job_count = 0;
    loop {
        job_tx.send(job_count).unwrap();
        job_count += LINES_PER_THREAD;
        if job_count >= HEIGHT {break;}
    }
    
    for i in 0..N_THREADS {
        let tx = tx.clone();
        let job_rx = Arc::clone(&job_rx);

        thread::spawn(move || {
            let lookfrom = Vector3f::new(13.0, 2.0, 3.0);
            let lookat = Vector3f::new(0.0, 0.0, 0.0);
            let vup = Vector3f::new(0.0, 1.0, 0.0);
            let distance_to_focus = 10.0;
            let aperture = 0.1;

            let seed: [u8; 32] = [1, 2, 3, 4,1, 2, 3, 4,1, 2, 3, 4,1, 2, 3, 4,1, 2, 3, 4,1, 2, 3, 4,1, 2, 3, 4,1, 2, 3, 4];

            let world = scene_random(&seed);
            let camera = Camera::new(lookfrom, lookat, vup, VFOV, ASPECT_RATIO, distance_to_focus, aperture);
            let mut rng = rand::thread_rng();

            let mut idx = job_rx.lock().unwrap().recv().unwrap();
            let mut fidx = idx + LINES_PER_THREAD - 1;

            while idx != CLOSE_THREAD {
                if fidx >= HEIGHT {fidx = HEIGHT - 1;};

                for x in 0..WIDTH {
                    for y in idx..=fidx {
                        let mut sum = Vector3f::new(0.0, 0.0, 0.0);

                        for _ in 0..SAMPLES {
                            let r1: f32 = rng.gen();
                            let r2: f32 = rng.gen();

                            let u = (r1 + x as f32) / WIDTH as f32;
                            let v = (r2 + (HEIGHT - y) as f32) / HEIGHT as f32;

                            let r = camera.get_ray(u, v);
                            
                            sum += color(&r, &world, 0);
                        }
                        let pixel = image::Rgb(colorize_gamma2(sum / SAMPLES as f32));
                        
                        // println!("done {} {}", x, y);

                        tx.send((x, y, pixel)).unwrap();
                    }
                }
                
                idx = job_rx.lock().unwrap().recv().unwrap();
                fidx = idx + LINES_PER_THREAD - 1;
            }
            println!("Thread {} terminated.", i);
        });
    }

    for i in 0..WIDTH*HEIGHT {
        
        if i % WIDTH == 0 {
            println!("{:.2}%", 100.0 * i as f32 / (WIDTH * HEIGHT) as f32);
        }

        match rx.recv() {
            Ok((x, y, pixel)) => imgbuf.put_pixel(x, y, pixel),
            _ => (),
        }
    }

    for i in 0..N_THREADS {
        job_tx.send(CLOSE_THREAD).unwrap();
    }

    imgbuf.save("teste.png").unwrap();
}


