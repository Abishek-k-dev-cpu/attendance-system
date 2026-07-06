export function Footer() {
  return (
    <footer className="mt-16 border-t border-border/60 bg-card/40">
      <div className="mx-auto grid max-w-7xl gap-6 px-4 py-10 sm:px-6 md:grid-cols-3">
        <div>
          <h4 className="font-display text-lg font-bold">Government College of Engineering Dharmapuri</h4>
          <p className="mt-2 text-sm text-muted-foreground">
            dharmapuri— 636704, Tamil Nadu, India
          </p>
        </div>
        <div className="text-sm text-muted-foreground">
          <h4 className="font-display text-sm font-semibold text-foreground">Contact</h4>
          <p className="mt-2">abi10.ak.lm@gmail.com</p>
          <p>+91 7339325507</p>
        </div>
        <div className="text-sm text-muted-foreground">
          <h4 className="font-display text-sm font-semibold text-foreground">Office Hours</h4>
          <p className="mt-2">Mon – Sat · 9:00 AM – 5:00 PM</p>
          <p>Portal updated daily by 6:00 PM</p>
        </div>
      </div>
      <div className="border-t border-border/60 py-4 text-center text-xs text-muted-foreground">
        © {new Date().getFullYear()} Government College of Engineering Dharmapuri. All rights reserved.
      </div>
    </footer>
  );
}
