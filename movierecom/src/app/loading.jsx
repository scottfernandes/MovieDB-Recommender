import { Lancelot } from 'next/font/google'
import React from 'react'
import { ClipLoader } from 'react-spinners'
const lancelot = Lancelot({ weight: ["400"], subsets: ["latin-ext"] });

export default function loading() {
  return (
    <div>
        <div className="loader bg-white flex items-center justify-center h-screen w-screen">
          <ClipLoader color="black" size={100} />
          <p className={`${lancelot.className} text-5xl`}>MovieDB</p>
        </div>
    </div>
  )
}
