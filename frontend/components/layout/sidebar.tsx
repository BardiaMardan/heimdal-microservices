"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useEffect, useRef } from "react";
import { gsap } from "gsap";

const navigation = [
  { name: "Dashboard", href: "/dashboard" },
  { name: "Devices", href: "/dashboard/devices" },
  { name: "Telemetry", href: "/dashboard/telemetry" },
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
        className="fixed left-0 top-16 bottom-0 z-40 w-60 overflow-y-auto border-r border-white/10 bg-black"
      >
        <nav className="flex flex-col p-6 space-y-1">
          {navigation.map((item) => {
            // "/dashboard" is an index route: match it exactly, or every
            // nested route (/dashboard/devices, ...) would also light it up,
            // leaving two links "active" at once.
            const isActive =
              item.href === "/dashboard"
                ? pathname === item.href
                : pathname === item.href ||
                  pathname?.startsWith(item.href + "/");
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onClose}
                className={cn(
                  "text-sm font-medium px-3 py-2 transition-all duration-200",
                  isActive
                    ? "bg-white/10 text-white border-l-2 border-white"
                    : "text-white/60 hover:bg-white/5 hover:text-white"
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
