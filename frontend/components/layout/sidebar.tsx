"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useEffect, useRef } from "react";
import { gsap } from "gsap";

const navigation = [
  { name: "Agent", href: "/dashboard/agent" },
  { name: "Scenes", href: "/dashboard/scenes" },
  { name: "Devices", href: "/dashboard/devices" },
  { name: "Logs", href: "/dashboard/logs" },
];

interface SidebarProps {
  isOpen: boolean;
  onClose?: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();
  const sidebarRef = useRef<HTMLElement>(null);
  const overlayRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (sidebarRef.current && overlayRef.current) {
      const isMobile = window.innerWidth < 1024;
      
      if (isMobile) {
        if (isOpen) {
          gsap.set(sidebarRef.current, { x: -240 });
          gsap.set(overlayRef.current, { opacity: 0, display: "block" });
          gsap.to(sidebarRef.current, {
            x: 0,
            duration: 0.3,
            ease: "power2.out",
          });
          gsap.to(overlayRef.current, {
            opacity: 1,
            duration: 0.2,
          });
        } else {
          gsap.to(sidebarRef.current, {
            x: -240,
            duration: 0.3,
            ease: "power2.in",
          });
          gsap.to(overlayRef.current, {
            opacity: 0,
            duration: 0.2,
            onComplete: () => {
              if (overlayRef.current) {
                overlayRef.current.style.display = "none";
              }
            },
          });
        }
      } else {
        gsap.set(sidebarRef.current, { x: 0 });
        overlayRef.current.style.display = "none";
      }
    }
  }, [isOpen]);

  return (
    <>
      <div
        ref={overlayRef}
        className="fixed inset-0 bg-black/50 z-30 lg:hidden"
        onClick={onClose}
        style={{ display: "none" }}
      />
      <aside
        ref={sidebarRef}
        className="fixed left-0 top-16 bottom-0 z-40 w-60 border-r border-white/10 bg-black lg:translate-x-0 lg:static"
      >
        <nav className="flex flex-col p-6 space-y-1">
          {navigation.map((item) => {
            const isActive =
              pathname === item.href || pathname?.startsWith(item.href + "/");
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onClose}
                className={cn(
                  "text-sm font-medium text-white/80 px-3 py-2 transition-all duration-200",
                  isActive
                    ? "text-white underline decoration-2 underline-offset-4"
                    : "hover:bg-white/10 hover:text-white"
                )}
              >
                {item.name}
              </Link>
            );
          })}
        </nav>
      </aside>
    </>
  );
}
