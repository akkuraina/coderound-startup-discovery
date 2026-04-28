import React, { ReactNode } from 'react';
import Navbar from './Navbar';
import { Toaster } from 'react-hot-toast';

interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-gradient-light pt-20">
        <div className="container mx-auto px-4 py-8">{children}</div>
      </main>
      <Toaster position="top-right" />
    </>
  );
};

export default Layout;
