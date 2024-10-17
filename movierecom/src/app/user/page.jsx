"use client"
import { Button } from "@/components/ui/button";
import { Inter, Lancelot, Poppins } from "next/font/google";
import Link from "next/link";
import { useSession } from "next-auth/react";
import { redirect, useRouter } from "next/navigation";
import axios from "axios";
import Footer from "../helpers/Footer";
import Navbar from "../helpers/Navbar";
import { useEffect, useState } from "react";
import { Carousel, CarouselContent, CarouselDots, CarouselItem } from "@/components/ui/carousel";
import MovieCard from "../helpers/MovieCard";

const poppins = Poppins({ subsets: ["latin"], weight: ["600", "300"] });
const inter = Inter({ subsets: ["latin"] });
const lancelot = Lancelot({ subsets: ["latin"], weight: ["400"] });

export default function Home() {
  const{data:session} = useSession()
   
  const router = useRouter()
  if (!session) {
    redirect('/api/auth/signin');
}
    const [movies,setMovies] = useState([])
    const [posters,setPosters] = useState([])
    const [ratings,setRatings] = useState([])
    useEffect(() => {
      
        axios.get(`http://localhost:5000/user?username=${session.user.email}`,{withCredentials:true})
        .then((response)=>{
            
            setMovies(response.data['movie_titles'])
            setPosters(response.data['movies_poster'])
            setRatings(response.data['movie_ratings'])
        })
        .catch((error)=>{
            console.log(error);
            
        })
    
     
    }, [])
    

  return (
    <div className="flex flex-col min-h-screen  text-white">
                  <Navbar/>

      <div className="relative">
        <img
          src="https://repository-images.githubusercontent.com/275336521/20d38e00-6634-11eb-9d1f-6a5232d0f84f"
          className="h-[400px] sm:h-[500px] lg:h-[700px] w-screen object-cover brightness-50"
          alt="MovieDB Hero"
        />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className={`${inter.className} text-center`}>
            <p className="text-4xl sm:text-5xl lg:text-6xl text-white">
              Welcome to{" "}
              <span className={`text-red-500 text-7xl font-bold ${lancelot.className}`}>
                MovieDB
              </span>
            </p>
            <p className="text-lg sm:text-xl lg:text-2xl text-white m-4 sm:mt-6">
              Get personalized movie recommendations and have an amazing
              experience.
            </p>
            <div className="mt-6 sm:mt-10">
              <Link href="/user/recom">
                <Button
                  variant="destructive"
                  className="mx-2 w-[25%]  h-10 sm:h-12"
                >
                  Search for Movies
                </Button>
              </Link>
             <Link href={'/about-us'}>
            
              </Link>
            </div>
          </div>
        </div>
        <div className="absolute inset-x-0 bottom-0 h-20 bg-gradient-to-t from-black opacity-50"></div>
      </div>

      <div className="movies mt-40">
        <p className="text-5xl text-center text-red-500 underline">Based on your Watchlist</p>
        <div className="castcards mt-10">
                <Carousel
                  className="w-full"
                  opts={{
                    slidesToScroll: 1,
                    dots: true,
                    responsive: [
                      {
                        breakpoint: 1024, // lg
                        settings: {
                          slidesToShow: 3,
                          slidesToScroll: 3,
                        },
                      },
                      {
                        breakpoint: 768, // md
                        settings: {
                          slidesToShow: 2,
                          slidesToScroll: 2,
                        },
                      },
                      {
                        breakpoint: 640, // sm
                        settings: {
                          slidesToShow: 1,
                          slidesToScroll: 1,
                        },
                      },
                    ],
                  }}
                >
                  <CarouselContent className="mx-5">
                    {movies.map(
                      (movie, index) =>
                        index > 0 && (
                          <CarouselItem
                            className="lg:basis-1/3 md:basis-1/2 sm:basis-full"
                            key={index}
                          >
                            <MovieCard
                              movie={movie}
                              poster={posters[index]}
                              rating={ratings[index]}
                              movieClick={() =>
                                router.push(
                                  `/user/recom/${encodeURIComponent(movie)}`
                                )
                              }
                            />
                          </CarouselItem>
                        )
                    )}
                  </CarouselContent>
                  <CarouselDots />
                </Carousel>
              </div>
      </div>
      <div className="mt-24">
        <Footer />
      </div>
    </div>
  );
}
